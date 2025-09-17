# 2025.1.0 - 2025-09-16

This release completes the next set of enhancements to sentinel-driven test renaming. Highlights:

- Add `--prefix` and `--fallback` CLI flags to control generated filename prefix and fallback domain used when no sentinel is found.
- Harden slug/token sanitization and validation:
	- Preserve token case but sanitize to the allowed character set [A-Za-z0-9_].
	- Replace invalid characters with underscores, collapse repeated underscores, trim leading/trailing underscores.
	- Validate sanitized token and fallback lengths after normalization (max 64 characters).
	- Truncate aggregated slugs to 64 characters and validate final proposed filenames to a 240-character limit.
- CLI & naming improvements:
	- `build_proposals` now accepts `prefix`, `fallback`, and `excludes` parameters and validates proposed names against a safe pattern.
	- `apply_renames` has stronger proposal validation and clearer error messages for invalid proposals or rename failures.
- Parser / import scanning:
	- Conservative, AST-based detection of dynamic imports (literals, simple concatenations, simple JoinedStrs) improved and covered by tests.
	- Member-fallback resolution: dotted member names like `pkg.module.Class` now resolve to `pkg.module` when appropriate.
- Tests & quality:
	- Added focused unit tests and end-to-end tests for CLI, parser, namer, and util helpers. The full test-suite passes locally.
	- Ran ruff fixes and tightened test expectations.

# 2025.0.0 - 2025-09-15

- Added import-following mode: aggregate sentinels from imported modules under a root package.
- Added CLI flags: `--import-root`, `--repo-root`, `--verbose`.
- Improved API: parser.find_imports_in_file, parser.aggregate_sentinels_for_test, util_helpers.resolve_module_to_paths.
- Added tests for import scanning, module resolution, and end-to-end naming.

