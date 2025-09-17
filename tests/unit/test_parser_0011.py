from pathlib import Path

from splurge_test_namer.parser import find_imports_in_file


def test_static_and_dynamic_imports(tmp_path: Path):
    src = (
        "import splurge_lazyframe_compare.submod\n"
        "import importlib\n"
        "importlib.import_module('splurge_lazyframe_compare.main')\n"
        "from importlib import import_module\n"
        "import_module('splurge_lazyframe_compare.helper')\n"
        "__import__('splurge_lazyframe_compare.dunder')\n"
        "import importlib.machinery\n"
        "loader = importlib.machinery.SourceFileLoader('mod', '/tmp/mod.py')\n"
        "loader.load_module('splurge_lazyframe_compare.loader')\n"
        "NAME = 'splurge_lazyframe_compare.const'\n"
        "import_module(NAME)\n"
        "A = 'splurge_lazyframe_compare'\n"
        "B = '.concat'\n"
        "C = A + B\n"
        "import_module(C)\n"
        "F = f'splurge_lazyframe_compare.fstr'\n"
        "import_module(F)\n"
    )
    p = tmp_path / "t.py"
    p.write_text(src)
    found = find_imports_in_file(p, "splurge_lazyframe_compare", repo_root=None)
    # Expected modules
    expected = {
        "splurge_lazyframe_compare.submod",
        "splurge_lazyframe_compare.main",
        "splurge_lazyframe_compare.helper",
        "splurge_lazyframe_compare.dunder",
        "splurge_lazyframe_compare.loader",
        "splurge_lazyframe_compare.const",
        "splurge_lazyframe_compare.concat",
        "splurge_lazyframe_compare.fstr",
    }
    assert expected.issubset(found)
