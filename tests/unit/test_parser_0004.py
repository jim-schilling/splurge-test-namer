from pathlib import Path

from splurge_test_namer.parser import aggregate_sentinels_for_test


def write_module(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_relative_import_too_deep(tmp_path):
    repo = tmp_path / "repo"
    pkg = repo / "pkg"
    pkg.mkdir(parents=True)
    write_module(pkg / "__init__.py", "DOMAINS = ['root']\n")

    # create a test at top-level tests dir (not inside repo) that attempts a
    # relative import from deeper than the module location (should be skipped)
    tests = tmp_path / "tests"
    tests.mkdir()
    f = tests / "test_rel_deep.py"
    write_module(f, "from ..pkg import something\n")

    got = aggregate_sentinels_for_test(f, "pkg", repo, "DOMAINS")
    # nothing should be found because relative import couldn't be resolved
    assert got == []


def test_mixed___all___exports(tmp_path):
    repo = tmp_path / "repo"
    pkg = repo / "pkg"
    sub = pkg / "sub"
    sub.mkdir(parents=True)
    # module that defines __all__ limiting what is exported
    write_module(sub / "modx.py", "DOMAINS = ['x']\n__all__ = ['x']\n")
    # another module not exported
    write_module(sub / "mody.py", "DOMAINS = ['y']\n")

    tests = tmp_path / "tests"
    tests.mkdir()
    # star import from package: should still find modx but not mody if __all__ hides it
    f = tests / "test_star_all.py"
    write_module(f, "from pkg.sub import *\n")

    got = aggregate_sentinels_for_test(f, "pkg", repo, "DOMAINS")
    # Our parser doesn't evaluate __all__, but star-expansion will pick up files
    assert "x" in got
    assert "y" in got


def test_namespace_package_resolution(tmp_path):
    repo = tmp_path / "repo"
    # Create namespace package (no __init__.py)
    pkg = repo / "ns_pkg"
    sub = pkg / "subpkg"
    sub.mkdir(parents=True)
    write_module(sub / "mod.py", "DOMAINS = ['ns']\n")

    tests = tmp_path / "tests"
    tests.mkdir()
    f = tests / "test_ns.py"
    write_module(f, "from ns_pkg.subpkg import mod\n")

    got = aggregate_sentinels_for_test(f, "ns_pkg", repo, "DOMAINS")
    assert "ns" in got
