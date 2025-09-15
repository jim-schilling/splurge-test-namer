import pytest

from splurge_test_namer.parser import read_sentinels_from_file, find_imports_in_file
from splurge_test_namer.exceptions import FileReadError, SentinelReadError


def test_read_sentinels_parse_error_uses_regex(tmp_path):
    p = tmp_path / "tests" / "test_parse_err.py"
    p.parent.mkdir(parents=True)
    # introduce a syntax error before the sentinel so ast.parse will fail
    p.write_text("def bad(:\nDOMAINS = ['after_parse_error']\n")
    vals = read_sentinels_from_file(p, "DOMAINS")
    assert vals == ["after_parse_error"]


def test_read_sentinels_raises_on_read_error(tmp_path, monkeypatch):
    p = tmp_path / "tests" / "test_read_err.py"
    p.parent.mkdir(parents=True)
    p.write_text("DOMAINS = ['x']\n")
    # monkeypatch the parser's safe_file_reader to raise FileReadError
    import splurge_test_namer.parser as parser_mod

    monkeypatch.setattr(parser_mod, "safe_file_reader", lambda path: (_ for _ in ()).throw(FileReadError("boom")))
    with pytest.raises(SentinelReadError):
        read_sentinels_from_file(p, "DOMAINS")


def test_find_imports_returns_empty_on_read_error(tmp_path, monkeypatch):
    p = tmp_path / "tests" / "test_read_err2.py"
    p.parent.mkdir(parents=True)
    p.write_text("import splurge_sql_tool.core\n")
    import splurge_test_namer.parser as parser_mod

    monkeypatch.setattr(parser_mod, "safe_file_reader", lambda path: (_ for _ in ()).throw(FileReadError("boom")))
    found = find_imports_in_file(p, "splurge_sql_tool")
    assert found == set()
