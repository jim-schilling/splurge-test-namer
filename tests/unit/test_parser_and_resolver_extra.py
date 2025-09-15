import textwrap

from splurge_test_namer.parser import read_sentinels_from_file
from splurge_test_namer.util_helpers import resolve_module_to_paths


def test_read_sentinels_regex_fallback(tmp_path):
    p = tmp_path / "tests" / "test_regex.py"
    p.parent.mkdir(parents=True)
    # write a file where AST parsing might not pick up (odd formatting)
    p.write_text(
        textwrap.dedent("""
    DOMAINS = [
        'one',
        "two",
    ]
    """)
    )
    vals = read_sentinels_from_file(p, "DOMAINS")
    assert sorted(vals) == ["one", "two"]


def test_resolve_module_fallback_search(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    # create file deep in repo that ends with name 'utils.py'
    deep = repo / "some" / "path" / "utils.py"
    deep.parent.mkdir(parents=True)
    deep.write_text("# utils")

    found = resolve_module_to_paths("splurge_sql_tool.utils", repo)
    assert any(p.samefile(deep) for p in found)
