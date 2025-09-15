"""Rename test modules based on their <sentinel> metadata.

Usage:
  python tools/rename_tests_by_sentinels.py [--root tests] [--apply] [--sentinel DOMAINS]

Default is a dry-run which prints "original | proposed". When --apply is used
the script will perform os.rename and print "[original] -> [new]" for each
rename.

Naming rule:
  test_<sentinel1>_<sentinel2>_<NNN>.py
where sentinels come from the module-level <sentinel> list (order preserved) and
NNN is a zero-padded 4-digit sequence per prefix.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
from pathlib import Path


def read_sentinels_from_file(path: Path, sentinel: str) -> list[str]:
    """Return the module-level <sentinel> as a list of strings, or empty list."""
    try:
        src = path.read_text(encoding="utf-8")
    except Exception:
        return []
    try:
        tree = ast.parse(src)
    except Exception:
        tree = None
    if tree is not None:
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == sentinel:
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            out: list[str] = []
                            for el in node.value.elts:
                                if isinstance(el, ast.Constant) and isinstance(el.value, str):
                                    out.append(el.value)
                            return out
                        return []
    # fallback: regex
    m = re.search(rf"^{sentinel}\s*=\s*\[(.*?)\]", src, re.S | re.M)
    if m:
        items = re.findall(r"['\"](.*?)['\"]", m.group(1))
        return items
    return []


def slug_sentinel_list(sentinels: list[str]) -> str:
    # join with underscore and sanitize to [a-z0-9_]
    joined = "_".join(d.strip().lower() for d in sentinels if d)
    # replace non-alnum with underscore
    cleaned = re.sub(r"[^a-z0-9_]+", "_", joined)
    # collapse multiple underscores
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        return "misc"
    return cleaned


def build_proposals(root: Path, sentinel: str) -> list[tuple[Path, Path]]:
    """Scan test files and return a list of (original_path, proposed_path).

    Proposed filenames are placed in the same directory as original files.
    Sequence numbers are assigned per prefix across the whole scan.
    """
    files: list[Path] = sorted(root.rglob("*.py"))
    # gather list of (file, prefix)
    groups: dict[str, list[Path]] = {}
    mapping: dict[Path, str] = {}
    for f in files:
        # Skip files in helper directories (they are package modules used by tests)
        # and skip non-test files (we only want to rename files that already
        # follow the `test_` prefix). This prevents renaming helpers and
        # special files like conftest.py.
        if any(part.lower() == "helpers" for part in f.parts):
            continue
        if not f.name.startswith("test_"):
            # skip conftest.py and other non-test modules
            continue
        domains = read_sentinels_from_file(f, sentinel)
        prefix = "test_" + slug_sentinel_list(domains)
        mapping[f] = prefix
        groups.setdefault(prefix, []).append(f)

    proposals: list[tuple[Path, Path]] = []
    # for each prefix, sort files to make deterministic sequence
    for prefix, flist in sorted(groups.items()):
        flist_sorted = sorted(flist, key=lambda p: str(p).lower())
        for idx, f in enumerate(flist_sorted, start=1):
            seq = f"{idx:04d}"
            new_name = f"{prefix}_{seq}.py"
            new_path = f.with_name(new_name)
            proposals.append((f, new_path))
    return proposals


def show_dry_run(proposals: list[tuple[Path, Path]]) -> None:
    print("DRY RUN - original | proposed")
    for orig, prop in proposals:
        print(f"{orig} | {prop.name}")


def apply_renames(proposals: list[tuple[Path, Path]]) -> None:
    # first ensure no target collisions outside of the rename set
    targets = {p for _, p in proposals}
    for t in targets:
        if t.exists() and t not in [o for o, _ in proposals]:
            print(f"ERROR: target exists and is not being renamed: {t}")
            raise SystemExit(1)

    for orig, prop in proposals:
        if orig == prop:
            continue
        # if prop exists and is one of the originals, it's fine; perform rename
        print(f"[{orig}] -> [{prop}]")
        prop.parent.mkdir(parents=True, exist_ok=True)
        os.replace(str(orig), str(prop))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rename test modules based on <sentinel> metadata")
    p.add_argument("--root", default="tests", help="Root tests directory to scan")
    p.add_argument("--apply", action="store_true", help="Apply the renames (default is dry-run)")
    p.add_argument("--sentinel", default="DOMAINS", help="Module-level sentinel list to read (default: DOMAINS)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root)
    sentinel = args.sentinel
    if not root.exists():
        print(f"Test root not found: {root}")
        raise SystemExit(1)
    proposals = build_proposals(root, sentinel)
    if not args.apply:
        show_dry_run(proposals)
        print(f"\nProposals: {len(proposals)} (use --apply to perform)")
        return
    # apply
    apply_renames(proposals)


if __name__ == "__main__":
    main()
