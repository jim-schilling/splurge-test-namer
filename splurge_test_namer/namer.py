"""namer.py
Naming logic and proposal building for test renamer tool."""

from pathlib import Path
from splurge_test_namer.parser import read_sentinels_from_file, aggregate_sentinels_for_test
from splurge_test_namer.util_helpers import safe_file_rglob, safe_file_renamer
from splurge_test_namer.exceptions import FileGlobError, FileRenameError, SplurgeTestNamerError
import re
from typing import List, Tuple, Optional

DOMAINS = ["namer"]


def slug_sentinel_list(sentinels: List[str]) -> str:
    """Join sentinels with underscores and sanitize to [a-z0-9_]."""
    joined = "_".join(d.strip().lower() for d in sentinels if d)
    cleaned = re.sub(r"[^a-z0-9_]+", "_", joined)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        return "misc"
    return cleaned


def build_proposals(
    root: Path,
    sentinel: str,
    root_import: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> List[Tuple[Path, Path]]:
    """Scan test files and return a list of (original_path, proposed_path).

    If root_import and repo_root are provided, aggregate sentinels from imported
    modules under that root when building prefixes.
    """
    try:
        files: List[Path] = sorted(safe_file_rglob(root, "*.py"))
    except FileGlobError as e:
        raise SplurgeTestNamerError(f"Failed to glob test files in {root}") from e
    groups: dict[str, List[Path]] = {}
    mapping: dict[Path, str] = {}
    for f in files:
        if any(part.lower() == "helpers" for part in f.parts):
            continue
        if not f.name.startswith("test_"):
            continue
        if root_import and repo_root:
            domains = aggregate_sentinels_for_test(f, root_import, repo_root, sentinel)
        else:
            domains = read_sentinels_from_file(f, sentinel)
        prefix = "test_" + slug_sentinel_list(domains)
        mapping[f] = prefix
        groups.setdefault(prefix, []).append(f)

    proposals: List[Tuple[Path, Path]] = []
    for prefix, flist in sorted(groups.items()):
        flist_sorted = sorted(flist, key=lambda p: str(p).lower())
        for idx, f in enumerate(flist_sorted, start=1):
            seq = f"{idx:04d}"
            new_name = f"{prefix}_{seq}.py"
            new_path = f.with_name(new_name)
            proposals.append((f, new_path))
    return proposals


def show_dry_run(proposals: List[Tuple[Path, Path]]) -> None:
    print("DRY RUN - original | proposed")
    for orig, prop in proposals:
        print(f"{orig} | {prop.name}")


def apply_renames(proposals: List[Tuple[Path, Path]]) -> None:
    targets = {p for _, p in proposals}
    for t in targets:
        if t.exists() and t not in [o for o, _ in proposals]:
            print(f"ERROR: target exists and is not being renamed: {t}")
            raise SplurgeTestNamerError(f"Target exists and is not being renamed: {t}")

    for orig, prop in proposals:
        if orig == prop:
            continue
        print(f"[{orig}] -> [{prop}]")
        try:
            safe_file_renamer(orig, prop)
        except FileRenameError as e:
            raise SplurgeTestNamerError(f"Failed to rename {orig} to {prop}") from e
