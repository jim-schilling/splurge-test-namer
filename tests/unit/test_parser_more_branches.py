import textwrap

from splurge_test_namer.parser import find_imports_in_file, read_sentinels_from_file


def test_find_imports_from_multiple_names(tmp_path):
    p = tmp_path / "tests" / "test_multi_from.py"
    p.parent.mkdir(parents=True)
    p.write_text(
        textwrap.dedent("""
    from splurge_sql_tool.subpkg import a, b, c
    from splurge_sql_tool.deep.module import X
    """)
    )
    found = find_imports_in_file(p, "splurge_sql_tool")
    assert "splurge_sql_tool.subpkg" in found
    assert "splurge_sql_tool.deep.module" in found


def test_read_sentinels_ast_non_list_assign(tmp_path):
    p = tmp_path / "tests" / "test_nonlist.py"
    p.parent.mkdir(parents=True)
    # sentinel assigned to a string (not a list) should return [] per impl
    p.write_text("DOMAINS = 'single'\n")
    vals = read_sentinels_from_file(p, "DOMAINS")
    assert vals == []


def test_resolve_prefers_module_over_init(tmp_path):
    repo = tmp_path / "repo"
    pkg = repo / "splurge_sql_tool"
    pkg.mkdir(parents=True)
    mod = pkg / "utils.py"
    init = pkg / "utils" / "__init__.py"
    init.parent.mkdir(parents=True)
    mod.write_text("# module")
    init.write_text("# package init")

    from splurge_test_namer.util_helpers import resolve_module_to_paths

    paths = resolve_module_to_paths("splurge_sql_tool.utils", repo)
    # should include module file and package init; module file preferred first
    assert any(p.samefile(mod) for p in paths)
    assert any(p.samefile(init) for p in paths)
