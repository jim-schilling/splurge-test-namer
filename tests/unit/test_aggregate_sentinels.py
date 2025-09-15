from splurge_test_namer.parser import aggregate_sentinels_for_test


def test_aggregate_sentinels_missing_module(tmp_path):
    repo = tmp_path / "repo"
    tests = repo / "tests"
    pkg = repo / "splurge_sql_tool"
    pkg.mkdir(parents=True)
    tests.mkdir(parents=True)

    # create a module that does not exist on disk (import only)
    t1 = tests / "test_missing.py"
    t1.write_text("from splurge_sql_tool.missing import something\n")

    sent = aggregate_sentinels_for_test(t1, "splurge_sql_tool", repo, "DOMAINS")
    assert sent == []


def test_aggregate_sentinels_multiple_modules(tmp_path):
    repo = tmp_path / "repo"
    tests = repo / "tests"
    pkg = repo / "splurge_sql_tool"
    pkg.mkdir(parents=True)
    tests.mkdir(parents=True)

    core = pkg / "core.py"
    core.write_text("DOMAINS = ['core']\n")
    utils = pkg / "utils.py"
    utils.write_text("DOMAINS = ['utils']\n")

    t1 = tests / "test_multi.py"
    t1.write_text("from splurge_sql_tool.core import Query\nimport splurge_sql_tool.utils\n")

    sent = aggregate_sentinels_for_test(t1, "splurge_sql_tool", repo, "DOMAINS")
    assert sent == ["core", "utils"]
