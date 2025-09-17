import pytest

from splurge_test_namer.parser import read_sentinels_from_file, find_imports_in_file
from splurge_test_namer.exceptions import SentinelReadError


def test_read_sentinels_regex_fallback(tmp_path):
    f = tmp_path / "mod.py"
    # invalid python but contains a bracketed list that regex can find
    f.write_text("some = 1\nDOMAINS = ['a', 'b']\nnot valid python \n\n")
    items = read_sentinels_from_file(f, "DOMAINS")
    assert "a" in items and "b" in items


def test_read_sentinels_file_missing(tmp_path):
    f = tmp_path / "nope.py"
    with pytest.raises(SentinelReadError):
        read_sentinels_from_file(f, "DOMAINS")


def test_find_imports_error_returns_empty(monkeypatch, tmp_path):
    f = tmp_path / "t.py"
    f.write_text("import x")
    # monkeypatch safe_file_reader to raise
    from splurge_test_namer import parser

    from splurge_test_namer.exceptions import FileReadError

    def fake_reader(p):
        raise FileReadError("boom")

    monkeypatch.setattr(parser, "safe_file_reader", fake_reader)
    found = find_imports_in_file(f, "pkg")
    assert found == set()
