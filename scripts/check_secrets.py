"""Focused credential scan of tracked files; prints locations, never values."""
import re
import subprocess
from pathlib import Path

PATTERNS = {
    "Anthropic API key": re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    "OpenAI-style key": re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{30,}"),
    "GitHub token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})"),
    "AWS access key ID": re.compile(r"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    "Private key": re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
    "Non-empty AI key assignment": re.compile(r"(?m)^[ \t]*(?:ANTHROPIC_API_KEY|OPENAI_API_KEY)[ \t]*=[ \t]*[^\s#][^\r\n]*"),
}


def findings(text):
    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            yield label, text.count("\n", 0, match.start()) + 1


def main():
    names = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    count = 0
    for name in filter(None, names):
        path = Path(name)
        if path.name == ".env" or path.name.endswith((".pem", ".p12", ".pfx", ".key")):
            print(f"{name}: prohibited credential file")
            count += 1
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, line in findings(content):
            print(f"{name}:{line}: {label}")
            count += 1
    if count:
        raise SystemExit(1)
    print("No matching credential patterns in tracked text files.")


if __name__ == "__main__":
    main()
