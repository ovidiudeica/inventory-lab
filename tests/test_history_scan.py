import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_deleted_credential_is_detected(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)
    git("init")
    git("config", "user.email", "fixture@users.noreply.github.com")
    git("config", "user.name", "Test fixture")
    fixture = tmp_path / "sample.txt"
    secret = "gh" + "p_" + "x" * 36
    fixture.write_text(secret)
    git("add", ".")
    git("commit", "-m", "Synthetic fixture")
    fixture.unlink()
    git("add", "-A")
    git("commit", "-m", "Delete fixture")
    result = subprocess.run([sys.executable, str(ROOT / "scripts/check_history.py")],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1
    assert "GitHub token" in result.stdout
    assert secret not in result.stdout
    assert "2 reachable commits" in result.stdout


def test_metadata_group_is_reported_without_address(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)
    git("init")
    git("config", "user.email", "private-fixture@example.invalid")
    git("config", "user.name", "Synthetic fixture")
    git("commit", "--allow-empty", "-m", "Synthetic metadata fixture")
    result = subprocess.run([sys.executable, str(ROOT / "scripts/check_history.py")],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0
    assert "1 other distinct addresses requiring owner review" in result.stdout
    assert "Metadata privacy review: REQUIRED" in result.stdout
    assert "private-fixture@example.invalid" not in result.stdout
