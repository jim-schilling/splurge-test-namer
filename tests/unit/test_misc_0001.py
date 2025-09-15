import json
import subprocess
from pathlib import Path


def write_coverage_xml(path: Path, line_rate: float):
    path.write_text(f'''<?xml version="1.0" ?>
<coverage line-rate="{line_rate:.6f}" branch-rate="0" version="" timestamp="0">
</coverage>
''')


def test_happy_path(tmp_path: Path):
    cov = tmp_path / "coverage.xml"
    out = tmp_path / "badge.json"
    write_coverage_xml(cov, 0.9406)

    # Run the script
    res = subprocess.run(
        ["python", "tools/update_coverage_badge.py", str(cov), str(out)], cwd=Path.cwd(), capture_output=True, text=True
    )
    assert res.returncode == 0
    # badge file written
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["label"] == "coverage"
    assert data["message"] == "94.06%"


def test_missing_coverage(tmp_path: Path):
    cov = tmp_path / "coverage.xml"
    out = tmp_path / "badge.json"

    res = subprocess.run(
        ["python", "tools/update_coverage_badge.py", str(cov), str(out)], cwd=Path.cwd(), capture_output=True, text=True
    )
    assert res.returncode == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["message"] == "unknown"
