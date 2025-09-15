"""cli.py
CLI entrypoint and argument parsing for test renamer tool."""

from pathlib import Path
import argparse

from splurge_test_namer.namer import build_proposals, show_dry_run, apply_renames

DOMAINS = ["cli"]


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the test renamer tool."""
    p = argparse.ArgumentParser(description="Rename test modules based on <sentinel> metadata")
    p.add_argument("--root", default="tests", help="Root tests directory to scan")
    p.add_argument("--apply", action="store_true", help="Apply the renames (default is dry-run)")
    p.add_argument("--sentinel", default="DOMAINS", help="Module-level sentinel list to read (default: DOMAINS)")
    p.add_argument("--root-import", default=None, help="Root import path to follow from tests (optional)")
    p.add_argument("--repo-root", default=None, help="Repository root path to resolve imports (optional)")
    p.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (debug)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root)
    sentinel = args.sentinel
    root_import = args.root_import
    repo_root = Path(args.repo_root) if args.repo_root else None
    from splurge_test_namer.util_helpers import configure_logging

    configure_logging(args.verbose)
    if not root.exists():
        print(f"Test root not found: {root}")
        raise SystemExit(1)
    proposals = build_proposals(root, sentinel, root_import=root_import, repo_root=repo_root)
    if not args.apply:
        show_dry_run(proposals)
        print(f"\nProposals: {len(proposals)} (use --apply to perform)")
        return
    apply_renames(proposals)


if __name__ == "__main__":
    main()
