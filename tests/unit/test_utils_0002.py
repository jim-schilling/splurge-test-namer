from splurge_test_namer.util_helpers import resolve_module_to_paths


def test_resolve_module_file_and_package(tmp_path):
    repo = tmp_path / "repo"
    core_file = repo / "splurge_sql_tool" / "core.py"
    pkg_init = repo / "splurge_sql_tool" / "utils" / "__init__.py"
    pkg_init.parent.mkdir(parents=True, exist_ok=True)
    core_file.parent.mkdir(parents=True, exist_ok=True)
    core_file.write_text("# core module")
    pkg_init.write_text("# utils package")

    paths = resolve_module_to_paths("splurge_sql_tool.core", repo)
    assert any(p.samefile(core_file) for p in paths)

    paths2 = resolve_module_to_paths("splurge_sql_tool.utils", repo)
    # should find __init__.py for utils
    assert any(p.samefile(pkg_init) for p in paths2)
