from pathlib import Path

from splurge_test_namer.parser import find_imports_in_file


def _write_and_find(src: str, tmp_path: Path, root_import: str):
    p = tmp_path / "tests" / "test_dyn.py"
    p.parent.mkdir(parents=True)
    p.write_text(src)
    return find_imports_in_file(p, root_import, repo_root=None)


def test_importlib_import_module_literal(tmp_path: Path):
    src = 'import importlib\nimportlib.import_module("splurge_lazyframe_compare.main")\n'
    found = _write_and_find(src, tmp_path, "splurge_lazyframe_compare")
    assert "splurge_lazyframe_compare.main" in found


def test_from_importlib_import_module_literal(tmp_path: Path):
    src = 'from importlib import import_module\nimport_module("splurge_lazyframe_compare.main")\n'
    found = _write_and_find(src, tmp_path, "splurge_lazyframe_compare")
    assert "splurge_lazyframe_compare.main" in found


def test_dunder_import_literal(tmp_path: Path):
    src = '__import__("splurge_lazyframe_compare.main")\n'
    found = _write_and_find(src, tmp_path, "splurge_lazyframe_compare")
    assert "splurge_lazyframe_compare.main" in found


def test_sourcefileloader_load_module_literal(tmp_path: Path):
    src = (
        "import importlib.machinery\n"
        'loader = importlib.machinery.SourceFileLoader("mod", "/tmp/mod.py")\n'
        'loader.load_module("splurge_lazyframe_compare.main")\n'
    )
    found = _write_and_find(src, tmp_path, "splurge_lazyframe_compare")
    assert "splurge_lazyframe_compare.main" in found
