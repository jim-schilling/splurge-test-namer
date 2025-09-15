# splurge-test-namer

A small tool to rename test modules based on module-level sentinel lists (e.g. `DOMAINS = ['core','utils']`).

Usage
-----
- Dry run: `python -m splurge_test_namer.cli --root tests`
- Apply renames: `python -m splurge_test_namer.cli --root tests --apply`
- Follow imports under a root package: `python -m splurge_test_namer.cli --root tests --root-import splurge_sql_tool --repo-root /path/to/repo`

New in 2025.0.0
---------------
- Import-following mode: aggregate sentinels from imported modules under a root package when proposing test filenames.
- CLI flags: `--root-import`, `--repo-root`, `--verbose`.

See `docs/README-DETAILS.md` for full API and design notes.
