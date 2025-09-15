#!/usr/bin/env python3
"""Generate a Shields-compatible coverage badge JSON from coverage.xml.

Usage:
  python tools/update_coverage_badge.py [coverage.xml] [out.json]

If the GITHUB_OUTPUT env var is present, the script will append
coverage_percent=<value> to that file so GitHub Actions steps can read it.
"""
from __future__ import annotations

import json
import sys
import os
from pathlib import Path
from typing import Optional


def compute_percent_from_coverage_xml(path: Path) -> Optional[float]:
    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(path)
        root = tree.getroot()
        line_rate = root.attrib.get("line-rate")
        if line_rate is None:
            return None
        return float(line_rate) * 100.0
    except Exception:
        return None


def choose_color(pct: Optional[float]) -> str:
    if pct is None:
        return "lightgrey"
    if pct >= 90.0:
        return "brightgreen"
    if pct >= 75.0:
        return "yellow"
    return "red"


def write_badge(out_path: Path, pct: Optional[float]):
    msg = "unknown" if pct is None else f"{pct:.2f}%"
    badge = {
        "schemaVersion": 1,
        "label": "coverage",
        "message": msg,
        "color": choose_color(pct),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(badge))


def write_github_output(pct: Optional[float]):
    github_out = Path(os.environ.get("GITHUB_OUTPUT", ""))
    if github_out and github_out.exists():
        val = "unknown" if pct is None else f"{pct:.2f}"
        with github_out.open("a") as fh:
            fh.write(f"coverage_percent={val}\n")


def main(argv: list[str]) -> int:
    cov_path = Path(argv[1]) if len(argv) > 1 else Path("coverage.xml")
    out_path = Path(argv[2]) if len(argv) > 2 else Path(".github/badges/coverage.json")

    pct = compute_percent_from_coverage_xml(cov_path) if cov_path.exists() else None
    write_badge(out_path, pct)
    # Also write to GITHUB_OUTPUT when running on Actions
    write_github_output(pct)

    # Print summary for local debugging
    if pct is None:
        print("coverage_percent=unknown")
    else:
        print(f"coverage_percent={pct:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
