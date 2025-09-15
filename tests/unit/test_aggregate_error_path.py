
from splurge_test_namer.parser import aggregate_sentinels_for_test
from splurge_test_namer.util_helpers import resolve_module_to_paths


def test_aggregate_handles_unreadable_module(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    tests = repo / "tests"
    pkg = repo / "splurge_sql_tool"
    pkg.mkdir(parents=True)
    tests.mkdir(parents=True)

    core = pkg / "core.py"
    core.write_text("DOMAINS = ['core']\n")

    t1 = tests / "test_badread.py"
    t1.write_text("import splurge_sql_tool.core\n")

    # make resolve_module_to_paths return the core path
    paths = resolve_module_to_paths("splurge_sql_tool.core", repo)
    assert any(p.samefile(core) for p in paths)

    # monkeypatch the parser's safe_file_reader (it was imported there) to raise FileReadError
    from splurge_test_namer.exceptions import FileReadError

    monkeypatch.setattr(
        "splurge_test_namer.parser.safe_file_reader", lambda p: (_ for _ in ()).throw(FileReadError("boom"))
    )

    sent = aggregate_sentinels_for_test(t1, "splurge_sql_tool", repo, "DOMAINS")
    # should handle the read error and return empty
    assert sent == []
