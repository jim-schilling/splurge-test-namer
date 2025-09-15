# 2025.0.0 - 2025-09-15

- Added import-following mode: aggregate sentinels from imported modules under a root package.
- Added CLI flags: `--root-import`, `--repo-root`, `--verbose`.
- Improved API: parser.find_imports_in_file, parser.aggregate_sentinels_for_test, util_helpers.resolve_module_to_paths.
- Added tests for import scanning, module resolution, and end-to-end naming.

