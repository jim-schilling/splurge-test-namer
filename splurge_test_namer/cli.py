"""Command-line interface for the splurge-test-namer tool.

This module provides the CLI entrypoint and argument parsing used to run
the test renamer from the command line.

Copyright (c) 2025 Jim Schilling
License: MIT

Functions:
    parse_args: Parse command line arguments.
    main: Entry point that builds proposals and optionally applies renames.
"""

from pathlib import Path
import argparse
import sys

from splurge_test_namer.namer import build_proposals, show_dry_run, apply_renames

DOMAINS = ["cli"]


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the test renamer tool.

    Returns:
        Namespace: Parsed command line arguments.
    """
    p = argparse.ArgumentParser(
        description="Rename test modules based on <sentinel> metadata",
        epilog=(
            "Examples:\n"
            "  Dry run: python -m splurge_test_namer.cli --root tests\n"
            "  Apply renames: python -m splurge_test_namer.cli --root tests --apply\n"
            "  Apply and overwrite existing targets: python -m splurge_test_namer.cli --root tests --apply --force"
        ),
    )
    p.add_argument("--root", default="tests", help="Root tests directory to scan")
    p.add_argument("--apply", action="store_true", help="Apply the renames (default is dry-run)")
    p.add_argument("--sentinel", default="DOMAINS", help="Module-level sentinel list to read (default: DOMAINS)")
    p.add_argument("--root-import", default=None, help="Root import path to follow from tests (optional)")
    p.add_argument("--repo-root", default=None, help="Repository root path to resolve imports (optional)")
    p.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (debug)")
    p.add_argument("--force", action="store_true", help="Allow overwriting existing files during rename operations")
    return p.parse_args()


def _is_valid_sentinel(name: str) -> bool:
    """Return True if ``name`` is a valid sentinel identifier.

    A valid sentinel starts with a letter or underscore and contains only
    letters, digits or underscores.

    Args:
        name: Candidate sentinel name.

    Returns:
        True if valid, False otherwise.
    """
    import re

    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name))


def _is_valid_root_import(name: str) -> bool:
    """Return True if ``name`` looks like a dotted Python package name.

    Example valid values: "package", "package.subpackage.module"
    """
    import re

    return bool(re.match(r"^([A-Za-z_][A-Za-z0-9_]*)(\.[A-Za-z_][A-Za-z0-9_]*)*$", name))


def main() -> None:
    """CLI entrypoint.

    Parse command line arguments, build rename proposals, and either print a
    dry-run or apply the proposed renames depending on flags.
    """
    try:
        args = parse_args()
    except SystemExit:
        # argparse raises SystemExit for ``-h/--help`` after printing help.
        # Treat ``--help`` as a graceful exit (return from main) so callers
        # that import and call ``main()`` don't receive an exception.
        if any(h in sys.argv for h in ("-h", "--help")):
            return
        raise
    root = Path(args.root)
    sentinel = args.sentinel
    # Normalize explicit empty strings to None so callers can pass --root-import ""
    root_import = args.root_import if args.root_import not in ("", None) else None
    repo_root = Path(args.repo_root) if args.repo_root else None
    from splurge_test_namer.util_helpers import configure_logging

    configure_logging(args.verbose)

    # Basic validations and sanitization
    if not root.exists() or not root.is_dir():
        print(f"Test root not found or not a directory: {root}")
        raise SystemExit(2)
    # sentinel should be a valid Python identifier (letters, digits, underscores, not starting with digit)
    if not isinstance(sentinel, str) or not sentinel:
        print("Invalid sentinel name")
        raise SystemExit(2)
    if not _is_valid_sentinel(sentinel):
        print(f"Invalid sentinel name: {sentinel}")
        raise SystemExit(2)
    # validate root_import format if provided
    if root_import and not _is_valid_root_import(root_import):
        print(f"Invalid root_import format: {root_import}")
        raise SystemExit(2)
    if repo_root is not None and (not repo_root.exists() or not repo_root.is_dir()):
        print(f"repo_root not found or not a directory: {repo_root}")
        raise SystemExit(2)

    proposals = build_proposals(root, sentinel, root_import=root_import, repo_root=repo_root)
    if not args.apply:
        show_dry_run(proposals)
        print(f"\nProposals: {len(proposals)} (use --apply to perform)")
        return
    # apply renames; pass force flag so caller can opt into overwrites
    apply_renames(proposals, force=args.force)


if __name__ == "__main__":
    main()
