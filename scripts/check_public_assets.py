"""Independent, bounded checks against upstream public package and model metadata.

No credentials, inference requests or executable package installation.
The checks attest to assets retrieved during CI, not every visitor's future download.
"""
import base64
import hashlib
import io
import json
import tarfile
from urllib.parse import urlparse

import httpx

MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
REV = "1aa2c784701448c41116d0470738b551c29a99d2"
VERSION = "3.8.1"
LIMIT = 200 * 1024 * 1024


def allowed(url):
    parsed = urlparse(str(url))
    host = parsed.hostname or ""
    return parsed.scheme == "https" and (
        host in {"registry.npmjs.org", "cdn.jsdelivr.net", "huggingface.co"}
        or host.endswith((".huggingface.co", ".hf.co", ".xethub.hf.co"))
    )


def get(client, url):
    for _ in range(8):
        if not allowed(url):
            raise RuntimeError("Unexpected asset host")
        with client.stream("GET", url) as response:
            if response.is_redirect:
                url = str(response.next_request.url)
                continue
            response.raise_for_status()
            data = bytearray()
            for chunk in response.iter_bytes():
                data.extend(chunk)
                if len(data) > LIMIT:
                    raise RuntimeError("Public asset exceeds size limit")
            return bytes(data)
    raise RuntimeError("Too many redirects")


def main():
    with httpx.Client(timeout=60, follow_redirects=False, trust_env=False) as client:
        meta = json.loads(get(client, f"https://registry.npmjs.org/@huggingface%2ftransformers/{VERSION}"))
        assert meta["version"] == VERSION
        assert meta["license"] == "Apache-2.0"
        dist = meta["dist"]
        package = get(client, dist["tarball"])
        integrity = "sha512-" + base64.b64encode(hashlib.sha512(package).digest()).decode()
        assert integrity == dist["integrity"], "npm archive integrity mismatch"
        with tarfile.open(fileobj=io.BytesIO(package), mode="r:gz") as archive:
            manifest = json.load(archive.extractfile("package/package.json"))
            entry = manifest.get("jsdelivr") or manifest.get("unpkg") or manifest.get("module")
            assert isinstance(entry, str)
            source = archive.extractfile("package/" + entry.removeprefix("./")).read()
        cdn = get(client, f"https://cdn.jsdelivr.net/npm/@huggingface/transformers@{VERSION}")
        assert source == cdn, "CDN entry differs from registry package"
        assert hashlib.sha256(cdn).hexdigest() == "aa5002b70e789798da263f5f99c62bd3e8fcd0c119258a493c40c180648365fa", "CDN entry changed since validated CI #25"
        print("Transformers.js registry integrity and CDN entry verified; SHA-256:", hashlib.sha256(cdn).hexdigest())
        info = json.loads(get(client, f"https://huggingface.co/api/models/{MODEL}/revision/{REV}?blobs=true"))
        assert info["sha"] == REV
        assert info["cardData"]["license"] == "apache-2.0"
        weight = next(item for item in info["siblings"] if item["rfilename"] == "onnx/model_q4.onnx")
        expected = weight["lfs"]["sha256"]
        raw = get(client, f"https://huggingface.co/{MODEL}/resolve/{REV}/onnx/model_q4.onnx")
        actual = hashlib.sha256(raw).hexdigest()
        assert actual == expected, "Model weight integrity mismatch"
        assert actual == "933577110303a2964096d19b6f15d3b4639bef7f99481ac0b61d9f3ad72f392a", "Pinned weight changed since validated CI #25"
        print("Pinned model q4 weights verified against upstream SHA-256:", actual)


if __name__ == "__main__":
    main()
