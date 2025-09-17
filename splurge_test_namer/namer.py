"""Naming utilities for building and applying rename proposals.

This module contains logic to read sentinel lists from test modules, build
deterministic rename proposals and apply them safely to the filesystem.

Copyright (c) 2025 Jim Schilling
License: MIT
"""

from pathlib import Path
from splurge_test_namer.parser import read_sentinels_from_file, aggregate_sentinels_for_test
from splurge_test_namer.util_helpers import safe_file_rglob, safe_file_renamer
from splurge_test_namer.exceptions import FileGlobError, FileRenameError, SplurgeTestNamerError
import re
from typing import Optional
import logging

DOMAINS = ["namer"]


def slug_sentinel_list(sentinels: list[str], fallback: str = "misc") -> str:
    """Create a sanitized slug from a list of sentinel strings.

    The slug joins non-empty sentinel strings with underscores, lowercases
    them, replaces non-alphanumeric characters with underscores, and trims
    repeated underscores. If the result is empty, returns the provided
    fallback (normalized) or the string "misc".

    Args:
        sentinels: Iterable of candidate sentinel strings.

    Returns:
        A sanitized single-word slug suitable for filenames.
    """
    # Preserve token case (tokens are case-sensitive) but sanitize to the
    # allowed character set [A-Za-z0-9_]. Replace invalid characters with
    # underscores, collapse multiple underscores, and trim leading/trailing
    # underscores.
    tokens: list[str] = []
    for t in (d for d in sentinels if d):
        tok = t.strip()
        # replace spaces/dashes with underscore first
        tok = re.sub(r"[\s-]+", "_", tok)
        # replace any disallowed char with underscore (preserve case)
        tok = re.sub(r"[^A-Za-z0-9_]+", "_", tok)
        tok = re.sub(r"_+", "_", tok).strip("_")
        if tok:
            tokens.append(tok)

    # Normalize fallback similarly to tokens but also ensure a default
    fb = (fallback or "misc").strip()
    fb = re.sub(r"[\s-]+", "_", fb)
    fb = re.sub(r"[^A-Za-z0-9_]+", "_", fb)
    fb = re.sub(r"_+", "_", fb).strip("_")
    if not fb:
        fb = "misc"

    # Validate sanitized token lengths: enforce max 64 characters on the
    # sanitized form (post-normalization). This prevents long tokens that
    # only become short after stripping invalid chars from slipping by.
    max_token_len = 64
    for tok in tokens:
        if len(tok) > max_token_len:
            raise SplurgeTestNamerError(
                f"Sentinel token too long after sanitization ({len(tok)} > {max_token_len}): {tok!r}"
            )

    # Validate sanitized fallback length
    if len(fb) > max_token_len:
        raise SplurgeTestNamerError(f"Fallback value too long after sanitization ({len(fb)} > {max_token_len}): {fb!r}")

    if not tokens:
        return fb

    joined = "_".join(tokens)

    # Truncate the aggregated slug to 64 characters;
    # the overall filename limit is enforced later. Remove trailing
    # underscores after truncation.
    max_slug_len = 64
    if len(joined) > max_slug_len:
        joined = joined[:max_slug_len].rstrip("_")

    if not joined:
        return fb

    return joined


def build_proposals(
    root: Path,
    sentinel: str,
    root_import: Optional[str] = None,
    repo_root: Optional[Path] = None,
    excludes: Optional[list[str]] = None,
    fallback: str = "misc",
    prefix: str = "test",
) -> list[tuple[Path, Path]]:
    """Scan test files and return a list of (original_path, proposed_path).

    If root_import and repo_root are provided, aggregate sentinels from imported
    modules under that root when building prefixes.
    """
    try:
        files: list[Path] = sorted(safe_file_rglob(root, "*.py"))
    except FileGlobError as e:
        raise SplurgeTestNamerError(f"Failed to glob test files in {root}") from e
    # Group proposals by file_prefix only so sequence numbers are global
    # across the provided root. The base name [PREFIX]_[SENTINEL-TOKENS]
    # must be unique across the test-root to avoid collisions.
    groups: dict[str, list[Path]] = {}
    mapping: dict[Path, str] = {}
    exclude_set = {e.lower() for e in (excludes or [])}
    for f in files:
        # skip helpers directories and any explicitly excluded directory names
        if any(part.lower() == "helpers" for part in f.parts):
            continue
        if exclude_set and any(part.lower() in exclude_set for part in f.parts):
            continue
        if not f.name.startswith("test_"):
            continue
        if root_import and repo_root:
            domains = aggregate_sentinels_for_test(f, root_import, repo_root, sentinel)
            # If aggregation via imports yielded nothing, fall back to reading
            # the module's own sentinel assignment so in-file DOMAINS are not
            # silently ignored. This covers cases where tests reference the
            # import-root but imported modules have no sentinels.
            logger = logging.getLogger(__name__)
            if not domains:
                logger.debug("aggregation returned empty for %s; falling back to in-file sentinel", f)
                domains = read_sentinels_from_file(f, sentinel)
        else:
            domains = read_sentinels_from_file(f, sentinel)
        # Compute prefix for this file and group it. Sequences are assigned
        # globally per prefix across the entire provided root. This requires
        # that the base name (prefix + slug) is unique across test-root.
        file_prefix = f"{prefix}_" + slug_sentinel_list(domains, fallback=fallback)
        mapping[f] = file_prefix
        groups.setdefault(file_prefix, []).append(f)

    proposals: list[tuple[Path, Path]] = []
    # Sort by prefix to produce deterministic ordering.
    for prefix, flist in sorted(groups.items(), key=lambda kv: kv[0]):
        flist_sorted = sorted(flist, key=lambda p: str(p).lower())
        for idx, f in enumerate(flist_sorted, start=1):
            seq = f"{idx:04d}"
            new_name = f"{prefix}_{seq}.py"
            # sanity check: prevent generating absurdly long filenames
            if len(new_name) > 240:
                raise SplurgeTestNamerError(
                    f"Proposed filename too long ({len(new_name)} > 240): {new_name!r} for original {f}"
                )
            # validate proposed name pattern: prefix + '_' + [A-Za-z0-9_]* + .py
            if not re.match(rf"^{re.escape(prefix)}_[A-Za-z0-9_]*\.py$", new_name):
                raise SplurgeTestNamerError(
                    f"Proposed filename does not match allowed pattern: {new_name!r} for original {f}"
                )
            new_path = f.with_name(new_name)
            proposals.append((f, new_path))
    return proposals


def show_dry_run(proposals: list[tuple[Path, Path]]) -> None:
    """Pretty-print a dry-run of rename proposals.

    Args:
        proposals: List of tuples (original_path, proposed_path).
    """
    print("DRY RUN - original | proposed")
    for orig, prop in proposals:
        print(f"{orig} | {prop.name}")


def apply_renames(proposals: list[tuple[Path, Path]], force: bool = False) -> None:
    """Apply rename proposals to the filesystem.

    This function validates the proposals list for conflicts and uses
    ``safe_file_renamer`` which performs pre-flight checks and avoids
    accidental overwrites by default.

    Args:
        proposals: List of (original_path, proposed_path) tuples.

    Raises:
        SplurgeTestNamerError: On validation failures or rename errors.
    """
    if not isinstance(proposals, list):
        raise SplurgeTestNamerError("Proposals must be a list")

    # Validate proposal structure early to avoid attribute errors when
    # consumers pass incorrect types (e.g., strings). Each proposal must be
    # a 2-tuple of Path objects.
    for item in proposals:
        if not (isinstance(item, tuple) and len(item) == 2):
            raise SplurgeTestNamerError("Invalid proposal format; expected tuples of (Path, Path)")
        o, p = item
        if not isinstance(o, Path) or not isinstance(p, Path):
            raise SplurgeTestNamerError("Invalid proposal paths; expected Path objects")

    targets = {p for _, p in proposals}
    origins = {o for o, _ in proposals}
    for t in targets:
        if t.exists() and t not in origins:
            if not force:
                raise SplurgeTestNamerError(f"Target exists and is not being renamed: {t}")
            # If force is enabled, allow overwriting existing targets that are
            # not part of the current origins. The underlying safe_file_renamer
            # will be invoked with overwrite=True when performing the rename.
            continue

    for orig, prop in proposals:
        if not isinstance(orig, Path) or not isinstance(prop, Path):
            raise SplurgeTestNamerError("Invalid proposal paths; expected Path objects")
        if orig == prop:
            continue

        # Prevent accidental rename across different drives on Windows
        try:
            if hasattr(orig, "drive") and hasattr(prop, "drive") and orig.drive != prop.drive:
                raise SplurgeTestNamerError(f"Source and destination are on different drives: {orig} -> {prop}")
        except Exception:
            # Best effort; continue if drive checks aren't applicable
            pass

        print(f"[{orig}] -> [{prop}]")
        try:
            # honor force flag
            safe_file_renamer(orig, prop, overwrite=force)
        except FileRenameError as e:
            raise SplurgeTestNamerError(f"Failed to rename {orig} to {prop}") from e
