"""Scan reachable Git snapshots and commit messages; never print credential values."""
import subprocess
from pathlib import PurePosixPath

from check_secrets import findings


def git(*args):
    return subprocess.check_output(["git", *args])


def scan_history():
    if git("rev-parse", "--is-shallow-repository").strip() != b"false":
        raise RuntimeError("Full history checkout is required")
    commits = git("rev-list", "--all", "HEAD").decode().splitlines()
    blobs = {}
    issues = 0
    binary = 0
    unusual_paths = set()
    service = set()
    other = {}
    github_service = {'noreply@github.com', 'support@github.com', 'actions@github.com', 'web-flow@github.com', 'dependabot@github.com'}
    for commit in commits:
        message = git("show", "-s", "--format=%B", commit).decode("utf-8", "replace")
        for label, line in findings(message):
            print(f"Commit {commit[:12]}, message line {line}: {label}")
            issues += 1
        emails = git("show", "-s", "--format=%ae%n%ce", commit).decode().splitlines()
        for role, email in zip(("author", "committer"), emails):
            email = email.strip().lower()
            if email.endswith("@users.noreply.github.com"):
                continue
            if email in github_service:
                service.add(email)
            else:
                other.setdefault(email, set()).add((commit[:12], role))
        for entry in git("ls-tree", "-r", "-z", commit).split(b"\0"):
            if not entry:
                continue
            meta, raw_path = entry.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            path = raw_path.decode("utf-8", "replace")
            name = PurePosixPath(path).name
            if name == ".env" or name.endswith((".pem", ".p12", ".pfx", ".key")):
                unusual_paths.add((oid, "prohibited credential filename"))
            if kind != "blob" or mode == "120000":
                unusual_paths.add((oid, "submodule or symlink requires review"))
            elif oid not in blobs:
                raw = git("cat-file", "blob", oid)
                blobs[oid] = True
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    binary += 1
                    continue
                for label, line in findings(text):
                    print(f"Blob {oid[:12]}, line {line}: {label}")
                    issues += 1
    for oid, reason in sorted(unusual_paths):
        print(f"Object {oid[:12]}: {reason}")
        issues += 1
    print(f"History: {len(commits)} reachable commits, {len(blobs)} distinct blobs, {binary} non-UTF-8 blobs.")
    print(f"Commit metadata: {len(service)} recognised GitHub service addresses; {len(other)} other distinct addresses requiring owner review.")
    for number, locations in enumerate(sorted(other.values(), key=lambda group: sorted(group)), 1):
        print(f"Metadata group {number}: " + ", ".join(f"{sha} ({role})" for sha, role in sorted(locations)))
    print("Metadata privacy review: " + ("REQUIRED — do not publish before owner review" if other else "No unrecognised addresses in scanned refs"))
    print(f"History credential findings: {issues}")
    return issues or binary


if __name__ == "__main__":
    raise SystemExit(bool(scan_history()))
