# Plan: Import-following sentinel scan

Date: 2025-09-15
Author: automated plan generator

Summary
-------
Add an optional import-following mode to the test renamer tool. When provided a root import path (for example `splurge_sql_tool`), the tool will scan test modules for imports that start with that root, resolve those imported modules to repository file paths, extract module-level sentinel lists from the imported modules, aggregate the sentinels into a deterministic sorted set, and use that set to generate test filename prefixes.

Goals
-----
- Accept a `root_import` parameter (CLI and programmatic API).
- For each test module, find all imports whose module path starts with `root_import`.
- Resolve those imported module names to filesystem paths within the repository workspace (support `package.__init__.py` and `module.py`).
- Read sentinel lists from the resolved module files and aggregate them per test file.
- Create a sorted, deduplicated sentinel list per test and use it to build file-name prefixes (e.g. `test_core_0001.py`, `test_sql_utils_0003.py`).
- Ensure unit and integration test filenames follow the same naming logic (e.g. `test_cli_0001.py`, `test_utils_0003.py`) when the repository under test uses the sentinel system.
- Keep behaviour backward-compatible when `root_import` is not provided.

Brief API (function signatures)
-------------------------------
- parser.find_imports_in_file(path: Path, root_import: str) -> set[str]
  - Parse AST of `path` and return dotted module names imported that start with `root_import`.
  - Example: from `tests/test_x.py` containing `from splurge_sql_tool.core import Query`, returns `{"splurge_sql_tool.core"}`.

- util_helpers.resolve_module_to_paths(module_name: str, repo_root: Path) -> list[Path]
  - Given a dotted module name, return candidate file paths in the repo (e.g., `splurge_sql_tool/core.py`, `splurge_sql_tool/core/__init__.py`).
  - Returns an empty list if none found.

- parser.aggregate_sentinels_for_test(test_path: Path, root_import: str, repo_root: Path, sentinel_name: str = "DOMAINS") -> list[str]
  - Find imports in `test_path` matching `root_import`, resolve each import to file(s), read sentinel lists from each resolved module, produce a sorted unique list of sentinels.
  - This will call `read_sentinels_from_file` for each resolved module file and aggregate results.

- namer.build_proposals(root: Path, sentinel: str = "DOMAINS", root_import: str | None = None, repo_root: Path | None = None) -> list[tuple[Path, Path]]
  - When `root_import` is provided, call `parser.aggregate_sentinels_for_test` per test file to build the prefix.
  - `repo_root` is used to resolve module import names to filesystem paths; default is project repository root.

Data shapes and behaviour contract
---------------------------------
- Inputs:
  - `root`: Path to tests directory to scan.
  - `root_import`: dotted root package string (optional).
  - `sentinel`: module-level variable name to read (default `DOMAINS`).
  - `repo_root`: repository root path for resolving imports.
- Outputs:
  - `build_proposals` returns list of tuples (original_path, proposed_path).
- Error modes:
  - Missing `repo_root` or test `root` -> `SystemExit(1)` via CLI; programmatic API should raise `SplurgeTestNamerError`.
  - Unresolvable module names -> ignored with a logged warning; continue.
  - Files with invalid syntax when reading sentinels -> skip that module and log warning; treat as no sentinels.
- Determinism:
  - Sorting rules: file discovery uses sorted list from rglob; import lists are sorted lexicographically; aggregated sentinel lists sorted alphabetically.
  - Sequence numbers are assigned in deterministic order per prefix across the whole scan.

Edge cases and handling
-----------------------
- Aliased imports (e.g., `import splurge_sql_tool as s`) — only the real dotted name is relevant; detect `Import` nodes and consider `name` attributes.
- `from splurge_sql_tool import core` and `from splurge_sql_tool.core import Query` — handle both `ImportFrom` and `Import` forms; reconstruct full module names.
- Multi-level imports (e.g., `from splurge_sql_tool.subpkg import module as m`) — use the full dotted path that starts with `root_import`.
- Wildcard imports (e.g., `from splurge_sql_tool.core import *`) — treat like `from splurge_sql_tool.core import` and resolve `splurge_sql_tool.core`.
- Dynamic imports (e.g., `importlib.import_module('splurge_sql_tool.' + mod)`) — ignore dynamic imports; they are out-of-scope.
- Missing modules on disk -> log a warning and continue; do not fail the entire run.
- Circular imports between modules -> resolution only follows module names statically; do not execute import logic or attempt to traverse import graphs beyond direct imports found in the test file.
- Packages vs modules -> prefer `module.py`, then `module/__init__.py`.
- Tests importing modules from virtualenv/external packages -> try to resolve within `repo_root` first; if not found, skip (we only care about code in the repository).
- Duplicate sentinel entries across multiple resolved modules -> dedupe and sort.

Acceptance criteria
-------------------
- Unit tests exist for `parser.find_imports_in_file` that cover `Import` and `ImportFrom` forms (aliases, `as` names, wildcard) and return only imports starting with `root_import`.
- Unit tests exist for `util_helpers.resolve_module_to_paths` validating resolution to `module.py` and `module/__init__.py` for packages and returning empty list for non-existent modules.
- Integration test: small simulated repo under `tmp_path` with package `splurge_sql_tool` having `core.py` and `utils.py`, tests importing those modules. Running `build_proposals` with `root_import='splurge_sql_tool'` produces proposals that include prefixes built from sentinels aggregated across imported modules.
 - Tests (unit and integration) should be named using the same sentinel-based naming rules when applicable; test fixtures used to simulate repositories should demonstrate that naming produces `test_<sentinels>_NNNN.py` style filenames.
- Behavior is backward-compatible when `root_import` omitted: the tool falls back to reading sentinels from the test module itself.
- Logged warnings for unresolvable modules appear but do not abort the run.

Testing strategy
----------------
- Use pytest with `tmp_path` fixtures to create small package trees.
- Tests:
  - Unit tests for AST import parsing — feed small source strings, parse, and assert expected module names.
  - Unit tests for module resolution — create files under `tmp_path`, call resolver, assert found paths.
  - Integration end-to-end test — write test file under `tmp_path/tests/` importing repo modules and ensure `build_proposals` returns deterministic proposals.
- Run tests locally with `pytest -q`.

Notes and next steps
--------------------
1. Implement `parser.find_imports_in_file` and unit tests.
2. Implement `util_helpers.resolve_module_to_paths`.
3. Implement `parser.aggregate_sentinels_for_test` using the existing `read_sentinels_from_file`.
4. Update `namer.build_proposals` to accept `root_import` and `repo_root` and use aggregated sentinels.
5. Add `--import-root` CLI flag to `cli.py` and update help documentation.

If you want, I can start implementing step 2 (add import scanner in `parser.py`) and mark that todo `in-progress`.