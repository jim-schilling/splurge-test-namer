"""parser.py
Sentinel extraction logic for test renamer tool."""

import ast
import re
from pathlib import Path
from splurge_test_namer.util_helpers import safe_file_reader, resolve_module_to_paths
from splurge_test_namer.exceptions import FileReadError, SentinelReadError
from typing import Set, List

DOMAINS = ["parser"]


def read_sentinels_from_file(path: Path, sentinel: str) -> List[str]:
    """Return the module-level <sentinel> as a list of strings, or empty list. Raises SentinelReadError on file read error."""
    try:
        src = safe_file_reader(path)
    except FileReadError as e:
        raise SentinelReadError(f"Failed to extract sentinels from {path}") from e
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
    # allow leading whitespace before the sentinel so indented assignments (e.g. inside blocks)
    m = re.search(rf"^\s*{sentinel}\s*=\s*\[(.*?)\]", src, re.S | re.M)
    if m:
        items = re.findall(r"['\"](.*?)['\"]", m.group(1))
        return items
    return []


def find_imports_in_file(path: Path, root_import: str) -> Set[str]:
    """Return dotted module names imported in `path` that start with `root_import`.

    Handles `import X`, `import X as Y`, `from X import Y`, and `from X.Y import Z`.
    """
    try:
        src = safe_file_reader(path)
    except FileReadError:
        return set()
    if not src:
        return set()
    try:
        tree = ast.parse(src)
    except Exception:
        return set()
    found: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith(root_import):
                    found.add(name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module
                # if level > 0, it's a relative import; skip
                if node.level and node.level > 0:
                    continue
                if mod.startswith(root_import):
                    found.add(mod)
    return found


def aggregate_sentinels_for_test(
    test_path: Path, root_import: str, repo_root: Path, sentinel_name: str = "DOMAINS"
) -> List[str]:
    """Aggregate sentinel lists from modules imported by `test_path` under `root_import`.

    Returns a sorted list of unique sentinel strings.
    """
    imports = find_imports_in_file(test_path, root_import)
    sentinels: Set[str] = set()
    for mod in sorted(imports):
        paths = resolve_module_to_paths(mod, repo_root)
        for p in paths:
            try:
                items = read_sentinels_from_file(p, sentinel_name)
            except SentinelReadError:
                items = []
            for it in items:
                sentinels.add(it)
    return sorted(sentinels)
