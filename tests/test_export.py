import json
import subprocess
import sys
from pathlib import Path

from inventory.build_demo import DEFAULT_OUTPUT, build_payload
from inventory.core import PROCEDURES, investigate, report, stock, summary


def test_export_matches_backend():
    payload = build_payload()
    assert payload["schema_version"] == 1
    assert payload["synthetic"] is True
    assert payload["stock"] == stock()
    assert payload["summary"] == summary()
    assert payload["procedures"] == PROCEDURES
    for row in stock():
        sku = row["sku"]
        assert payload["cases"][sku] == investigate(sku)
        assert payload["reports"][sku] == report(sku)
    assert json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")) == payload


def test_export_cli_and_stale_detection(tmp_path: Path):
    path = tmp_path / "demo.json"
    command = [sys.executable, "-m", "inventory.build_demo", "--output", str(path)]
    subprocess.run(command, check=True)
    assert json.loads(path.read_text(encoding="utf-8")) == build_payload()
    subprocess.run(command + ["--check"], check=True)
    path.write_text("{}", encoding="utf-8")
    assert subprocess.run(command + ["--check"]).returncode == 1
