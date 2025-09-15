from splurge_test_namer.parser import find_imports_in_file


def test_relative_import_ignored(tmp_path):
    p = tmp_path / "tests" / "test_rel.py"
    p.parent.mkdir(parents=True)
    p.write_text("from . import core\n")
    found = find_imports_in_file(p, "splurge_sql_tool")
    assert found == set()


def test_invalid_syntax_returns_empty(tmp_path):
    p = tmp_path / "tests" / "test_bad.py"
    p.parent.mkdir(parents=True)
    p.write_text("def foo(:\n")
    found = find_imports_in_file(p, "splurge_sql_tool")
    assert found == set()
