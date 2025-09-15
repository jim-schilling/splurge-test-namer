from splurge_test_namer.namer import build_proposals


def test_end_to_end_naming(tmp_path):
    # create a fake repo layout
    repo = tmp_path / "repo"
    tests = repo / "tests"
    pkg = repo / "splurge_sql_tool"
    (pkg).mkdir(parents=True)
    (tests).mkdir(parents=True)

    # create modules with DOMAINS
    core = pkg / "core.py"
    core.write_text("DOMAINS = ['core','sql']\n")
    utils = pkg / "utils.py"
    utils.write_text("DOMAINS = ['utils']\n")

    # create test files importing those modules
    t1 = tests / "test_a.py"
    t1.write_text("from splurge_sql_tool.core import Query\n")
    t2 = tests / "test_b.py"
    t2.write_text("import splurge_sql_tool.utils as u\n")
    t3 = tests / "test_c.py"
    t3.write_text("# no imports\nDOMAINS = ['misc']\n")

    proposals = build_proposals(tests, "DOMAINS", root_import="splurge_sql_tool", repo_root=repo)
    # expect proposals to be created with prefixes using aggregated sentinels
    names = [p.name for _, p in proposals]
    assert any(n.startswith("test_core_sql_") for n in names)
    assert any(n.startswith("test_utils_") for n in names)
    assert any(n.startswith("test_misc_") for n in names)
