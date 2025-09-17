from splurge_test_namer.parser import (
    read_sentinels_from_file,
    find_imports_in_file,
    aggregate_sentinels_for_test,
)
from splurge_test_namer.exceptions import SentinelReadError


def test_read_sentinels_non_list_and_mixed_items(tmp_path):
    f1 = tmp_path / "m1.py"
    f1.write_text("DOMAINS = 'notalist'\n")
    assert read_sentinels_from_file(f1, "DOMAINS") == []

    f2 = tmp_path / "m2.py"
    f2.write_text("DOMAINS = [1, 'ok', None]\n")
    items = read_sentinels_from_file(f2, "DOMAINS")
    assert items == ["ok"]


def test_find_imports_ast_error_returns_empty(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("def bad:\n")
    found = find_imports_in_file(f, "pkg")
    assert found == set()


def test_find_imports_relative_without_repo_root(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("from .sub import mod\n")
    found = find_imports_in_file(f, "pkg")
    assert found == set()


def test_find_imports_relative_level_too_deep(tmp_path):
    repo = tmp_path / "repo"
    # create a file two levels deep
    p = repo / "a" / "t.py"
    p.parent.mkdir(parents=True)
    p.write_text("from ...sub import mod\n")
    # base_parts length is 2 (a.t) and node.level==3 therefore should skip
    found = find_imports_in_file(p, "pkg", repo)
    assert found == set()


def test_find_imports_from_alias(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("from pkg import sub as s\n")
    found = find_imports_in_file(f, "pkg")
    assert "pkg.sub" in found


def test_aggregate_handles_sentinelreaderror(monkeypatch, tmp_path):
    # create a test that imports pkg.mod
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = tmp_path / "tests"
    tests.mkdir()
    testf = tests / "test_x.py"
    testf.write_text("from pkg import mod\n")

    # monkeypatch resolve_module_to_paths to return a fake path
    fake_path = repo / "pkg" / "mod.py"
    fake_path.parent.mkdir(parents=True, exist_ok=True)
    fake_path.write_text("# content")

    from splurge_test_namer import parser

    monkeypatch.setattr(parser, "resolve_module_to_paths", lambda mod, rr: [fake_path])

    def fake_read(p, s):
        raise SentinelReadError("boom")

    monkeypatch.setattr(parser, "read_sentinels_from_file", fake_read)

    got = aggregate_sentinels_for_test(testf, "pkg", repo, "DOMAINS")
    assert got == []
