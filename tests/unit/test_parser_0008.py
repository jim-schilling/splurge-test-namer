from pathlib import Path

from splurge_test_namer.parser import find_imports_in_file


def _write_and_find(src: str, tmp_path: Path, root_import: str, repo_root=None):
    p = tmp_path / "pkg" / "tests" / "test_file.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(src)
    return find_imports_in_file(p, root_import, repo_root=repo_root)


def test_relative_from_import_resolution(tmp_path: Path):
    # Create package structure: tmp_path/pkg/sub/mod.py and package __init__
    # Use repo_root=tmp_path so base_module becomes 'pkg.tests.test_file' and
    # relative imports climb up into 'pkg'.
    repo_root = tmp_path
    pkg_dir = repo_root / "pkg"
    (pkg_dir / "sub").mkdir(parents=True)
    (pkg_dir / "sub" / "mod.py").write_text("")
    (pkg_dir / "__init__.py").write_text("")

    # in tests/test_file.py, use from ..sub import mod with level=2 (..)
    src = """
from ..sub import mod
"""
    found = _write_and_find(src, tmp_path, "pkg", repo_root=repo_root)
    # The resolved module should be 'pkg.sub' or 'pkg.sub.mod' depending on handling;
    # parser records the module (mod) as parent when resolving relative imports.
    assert any(name.startswith("pkg.sub") for name in found)


def test_star_import_expansion(tmp_path: Path):
    # create package dir with multiple .py files
    repo_root = tmp_path
    pkg_dir = repo_root / "mypkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("")
    (pkg_dir / "a.py").write_text("")
    (pkg_dir / "b.py").write_text("")

    src = """
from mypkg import *
"""
    # place test file under repo_root so relative expansion can search package dir
    p = repo_root / "tests" / "test_file.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(src)
    found = find_imports_in_file(p, "mypkg", repo_root=repo_root)
    # expansion should include mypkg.a and mypkg.b or at least mypkg
    assert any(n.startswith("mypkg") for n in found)


def test_loader_variable_and_load_module(tmp_path: Path):
    # create a source that assigns loader = importlib.machinery.SourceFileLoader(...)
    src = """
import importlib.machinery
loader = importlib.machinery.SourceFileLoader('mod', '/tmp/x')
loader.load_module('mypkg.loaded')
"""
    found = _write_and_find(src, tmp_path, "mypkg")
    assert any(n.startswith("mypkg.loaded") for n in found)
