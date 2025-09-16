"""Sentinel extraction and import scanning utilities.

This module provides helpers to read module-level sentinel lists and to
find imports inside test modules so sentinels can be aggregated from
imported code under a project root.

Copyright (c) 2025 Jim Schilling
License: MIT
"""

import ast
import logging
import re
from pathlib import Path
from typing import Set, Optional

from splurge_test_namer.util_helpers import (
    safe_file_reader,
    resolve_module_to_paths_with_member_fallback,
)
from splurge_test_namer.exceptions import FileReadError, SentinelReadError

DOMAINS = ["parser"]


def _eval_constant_string_binop(node: ast.AST, const_map: Optional[dict[str, str]] = None) -> Optional[str]:
    """Evaluate simple string concatenation BinOp nodes composed of Constant strings.

    Returns the concatenated string or None if it cannot be resolved.
    """
    # only support left-heavy chains of BinOp with Add and Constant string nodes
    if not isinstance(node, ast.BinOp):
        return None
    if not isinstance(node.op, ast.Add):
        return None

    def eval_node(n: ast.AST) -> Optional[str]:
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            return n.value
        if isinstance(n, ast.Name) and const_map is not None:
            return const_map.get(n.id)
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
            left = eval_node(n.left)
            right = eval_node(n.right)
            if left is not None and right is not None:
                return left + right
        return None

    return eval_node(node)


def read_sentinels_from_file(path: Path, sentinel: str) -> list[str]:
    """Extract a module-level sentinel list from a Python source file.

    The function first tries to parse the module AST to find a top-level
    assignment named ``sentinel`` with a list or tuple of string constants.
    If AST parsing fails or no assignment is found, a permissive regex
    fallback is used to locate a bracketed list in the source.

    Args:
        path: Filesystem path to the Python module.
        sentinel: Variable name to search for (e.g. "DOMAINS").

    Returns:
        A list of string values found in the sentinel assignment, or an
        empty list if none were found.

    Raises:
        SentinelReadError: If reading the file contents fails.
    """
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
            # Handle simple assignments: SENTINEL = ['a', 'b']
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == sentinel:
                        val = node.value
                        if isinstance(val, (ast.List, ast.Tuple)):
                            out: list[str] = []
                            for el in val.elts:
                                if isinstance(el, ast.Constant) and isinstance(el.value, str):
                                    out.append(el.value)
                            return out
                        return []

            # Handle annotated assignments (PEP 526): SENTINEL: list[str] = ['a']
            if isinstance(node, ast.AnnAssign):
                target = node.target
                if isinstance(target, ast.Name) and target.id == sentinel:
                    # value may be None if only annotation provided; we only
                    # accept cases with an explicit value that's a list/tuple
                    ann_val = node.value
                    if isinstance(ann_val, (ast.List, ast.Tuple)):
                        out_items: list[str] = []
                        for el in ann_val.elts:
                            if isinstance(el, ast.Constant) and isinstance(el.value, str):
                                out_items.append(el.value)
                        return out_items
                    return []

    # fallback: regex
    # allow leading whitespace before the sentinel so indented assignments (e.g. inside blocks)
    # Regex fallback: accept optional type annotation between the name and '='
    # Examples matched:
    #  DOMAINS = ['a']
    #  DOMAINS: list[str] = ['a']
    m = re.search(rf"^\s*{sentinel}(?:\s*:\s*[A-Za-z0-9_\[\],\. ]+)?\s*=\s*\[(.*?)\]", src, re.S | re.M)
    if m:
        items = re.findall(r"['\"](.*?)['\"]", m.group(1))
        return items
    return []


def find_imports_in_file(path: Path, root_import: str, repo_root: Optional[Path] = None) -> Set[str]:
    """Return dotted module names imported in `path` that start with `root_import`.

    Handles `import X`, `import X as Y`, `from X import Y`, and `from X.Y import Z`.
    Also recognizes a limited set of dynamic imports where the module name is a
    string literal: importlib.import_module('pkg.mod'), __import__('pkg.mod'),
    or loader.load_module('pkg.mod') where the loader variable was created via
    importlib.machinery.SourceFileLoader(...).
    """
    logger = logging.getLogger(__name__)

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
    # Map variable names that are assigned to importlib SourceFileLoader(...) so
    # we can recognize subsequent loader.load_module(...) calls as dynamic imports.
    loader_vars: set[str] = set()
    # Map simple NAME = "literal" assignments so we can resolve names passed
    # to dynamic import functions when the name is a constant string.
    const_string_vars: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            # only simple assignments: NAME = Call(...)
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name):
                continue
            val = node.value
            if isinstance(val, ast.Call) and isinstance(val.func, (ast.Attribute, ast.Name)):
                # build dotted name of the constructor
                def dotted_from(n: ast.AST) -> Optional[str]:
                    dotted_parts: list[str] = []
                    cur = n
                    while True:
                        if isinstance(cur, ast.Name):
                            dotted_parts.append(cur.id)
                            break
                        if isinstance(cur, ast.Attribute):
                            dotted_parts.append(cur.attr)
                            cur = cur.value
                            continue
                        return None
                    return ".".join(reversed(dotted_parts))

                dotted = dotted_from(val.func)
                if dotted and "SourceFileLoader" in dotted and dotted.split(".")[0] == "importlib":
                    loader_vars.add(target.id)
            # capture simple constant string assignments: NAME = 'pkg.mod'
            elif isinstance(val, ast.Constant) and isinstance(val.value, str):
                const_string_vars[target.id] = val.value
            # capture simple concatenations of constants or names: NAME = 'a' + '.b' or A + B
            elif isinstance(val, ast.BinOp):
                resolved = _eval_constant_string_binop(val, const_string_vars)
                if resolved is not None:
                    const_string_vars[target.id] = resolved
            # capture simple f-strings with only constant parts (JoinedStr)
            elif isinstance(val, ast.JoinedStr):
                joined_parts: list[str] = []
                ok = True
                for v in val.values:
                    if isinstance(v, ast.Constant) and isinstance(v.value, str):
                        joined_parts.append(v.value)
                    else:
                        ok = False
                        break
                if ok:
                    const_string_vars[target.id] = "".join(joined_parts)

    # Determine base module name for relative import resolution if repo_root provided
    base_module: Optional[str] = None
    try:
        if repo_root is not None and path.is_relative_to(repo_root):
            rel = path.relative_to(repo_root).with_suffix("")
            base_module = ".".join(rel.parts)
    except Exception:
        base_module = None

    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for alias in n.names:
                name = alias.name
                if name.startswith(root_import):
                    logger.debug("static import detected: %s", name)
                    found.add(name)

        elif isinstance(n, ast.ImportFrom):
            # n.module may be None for constructs like `from . import name`.
            mod = n.module
            # if level > 0, it's a relative import; attempt to resolve
            if n.level and n.level > 0:
                # Resolve relative import against the base module if available
                if base_module is None:
                    continue
                base_parts = base_module.split(".")
                # climb up `level` parts
                if n.level > len(base_parts):
                    continue
                parent = ".".join(base_parts[: -n.level])
                if mod:
                    # from ..mod import name -> parent.mod and parent.mod.name
                    full_mod = f"{parent}.{mod}" if parent else mod
                else:
                    # from .. import name -> parent
                    full_mod = parent
                if full_mod and full_mod.startswith(root_import):
                    logger.debug("from-import (relative resolved) detected: %s", full_mod)
                    found.add(full_mod)
                for alias in n.names:
                    if alias.name == "*":
                        # Expand star imports by listing submodules under the
                        # package directory when repo_root is available.
                        if repo_root is not None and mod:
                            try:
                                pkg_dir = repo_root.joinpath(*mod.split("."))
                                if pkg_dir.exists() and pkg_dir.is_dir():
                                    for child in pkg_dir.iterdir():
                                        if child.suffix == ".py" and child.name != "__init__.py":
                                            candidate = f"{mod}.{child.stem}"
                                            if candidate.startswith(root_import):
                                                logger.debug("star-import expansion candidate: %s", candidate)
                                                found.add(candidate)
                            except Exception:
                                pass
                        # also keep the module or parent so __init__ can be inspected
                        logger.debug("from-import star keep module: %s", mod or full_mod)
                        if mod:
                            found.add(mod)
                        elif full_mod:
                            found.add(full_mod)
                        continue
                    candidate = f"{full_mod}.{alias.name}" if full_mod else alias.name
                    if candidate.startswith(root_import):
                        logger.debug("from-import alias detected: %s", candidate)
                        found.add(candidate)
            else:
                # Non-relative from-import
                if mod and mod.startswith(root_import):
                    logger.debug("from-import module detected: %s", mod)
                    found.add(mod)
                # Also handle 'from pkg import submodule' -> record 'pkg.submodule'
                for alias in n.names:
                    if alias.name == "*":
                        if repo_root is not None and mod:
                            try:
                                pkg_dir = repo_root.joinpath(*mod.split("."))
                                if pkg_dir.exists() and pkg_dir.is_dir():
                                    for child in pkg_dir.iterdir():
                                        if child.suffix == ".py" and child.name != "__init__.py":
                                            candidate = f"{mod}.{child.stem}"
                                            if candidate.startswith(root_import):
                                                logger.debug("star-import expansion candidate: %s", candidate)
                                                found.add(candidate)
                            except Exception:
                                pass
                        logger.debug("from-import star keep module: %s", mod)
                        if mod:
                            found.add(mod)
                        continue
                    if not mod:
                        # from X import name where X is None is unusual for
                        # non-relative imports; skip defensively
                        continue
                    candidate = f"{mod}.{alias.name}"
                    if candidate.startswith(root_import):
                        logger.debug("from-import candidate detected: %s", candidate)
                        found.add(candidate)

        # detect dynamic import calls like importlib.import_module("pkg.mod")
        elif isinstance(n, ast.Call):
            func = n.func
            is_import_call = False

            def dotted_name_from_attr(attr_node: ast.AST) -> Optional[str]:
                """Return dotted name for nested ast.Attribute/ast.Name or None."""
                attr_parts: list[str] = []
                cur = attr_node
                while True:
                    if isinstance(cur, ast.Name):
                        attr_parts.append(cur.id)
                        break
                    if isinstance(cur, ast.Attribute):
                        attr_parts.append(cur.attr)
                        cur = cur.value
                        continue
                    return None
                return ".".join(reversed(attr_parts))

            # handle attribute-style calls (importlib.import_module, importlib.machinery.SourceFileLoader.load_module)
            if isinstance(func, ast.Attribute):
                dotted = dotted_name_from_attr(func)
                # dotted will be like 'importlib.import_module' or 'importlib.machinery.SourceFileLoader.load_module'
                if dotted:
                    if dotted.endswith("import_module"):
                        # require 'importlib' to appear in the dotted path
                        if dotted.split(".")[0] == "importlib":
                            is_import_call = True
                    elif dotted.endswith("load_module"):
                        lead = dotted.split(".")[0]
                        # either importlib.machinery.SourceFileLoader.load_module
                        # or a variable name assigned earlier to a SourceFileLoader
                        if lead == "importlib" or lead in loader_vars:
                            is_import_call = True
                else:
                    # handle loader.load_module('...') where loader was created earlier
                    if isinstance(func.value, ast.Name) and func.attr == "load_module":
                        if func.value.id in loader_vars:
                            is_import_call = True
            # name-style calls: __import__, import_module
            elif isinstance(func, ast.Name):
                if func.id in ("__import__", "import_module"):
                    is_import_call = True

            if is_import_call and n.args:
                first = n.args[0]
                modname: Optional[str] = None
                # literal string
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    modname = first.value
                # simple name referencing a literal assigned above
                elif isinstance(first, ast.Name) and first.id in const_string_vars:
                    modname = const_string_vars[first.id]
                # simple concatenation of constants
                elif isinstance(first, ast.BinOp):
                    modname = _eval_constant_string_binop(first)
                # f-strings (JoinedStr) with only constant parts
                elif isinstance(first, ast.JoinedStr):
                    call_joined_parts: list[str] = []
                    ok = True
                    for v in first.values:
                        if isinstance(v, ast.Constant) and isinstance(v.value, str):
                            call_joined_parts.append(v.value)
                        else:
                            ok = False
                            break
                    if ok:
                        modname = "".join(call_joined_parts)

                if modname:
                    if modname.startswith(root_import):
                        logger.debug("dynamic import detected (literal/const): %s", modname)
                        found.add(modname)
                    lead = modname.split(".")[0]
                    if lead.startswith(root_import):
                        logger.debug("dynamic import detected by leading component: %s", modname)
                        found.add(modname)
    return found


def aggregate_sentinels_for_test(
    test_path: Path, root_import: str, repo_root: Path, sentinel_name: str = "DOMAINS"
) -> list[str]:
    """Aggregate sentinel lists from modules imported by `test_path` under `root_import`.

    Returns a sorted list of unique sentinel strings.
    """
    imports = find_imports_in_file(test_path, root_import, repo_root)
    sentinels: Set[str] = set()
    for mod in sorted(imports):
        # Use the member-fallback resolver so dotted member names like
        # 'pkg.module.Class' will resolve to 'pkg.module' when possible.
        paths = resolve_module_to_paths_with_member_fallback(mod, repo_root)
        for p in paths:
            try:
                items = read_sentinels_from_file(p, sentinel_name)
            except SentinelReadError:
                items = []
            for it in items:
                sentinels.add(it)
    return sorted(sentinels)
