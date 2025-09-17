from splurge_test_namer.parser import find_imports_in_file, aggregate_sentinels_for_test


def test_relative_from_named_alias(tmp_path):
    # repo/pkg/tests/test.py with 'from .sub import mod' -> should resolve to pkg.tests.sub.mod
    repo = tmp_path / "repo"
    pkg_tests = repo / "pkg" / "tests"
    sub = pkg_tests / "sub"
    sub.mkdir(parents=True)
    # create the module that will contain the sentinel
    mod = sub / "mod.py"
    mod.write_text("DOMAINS = ['rmod']\n")

    testf = pkg_tests / "test_rel_named.py"
    testf.parent.mkdir(parents=True, exist_ok=True)
    testf.write_text("from .sub import mod\n")

    got = aggregate_sentinels_for_test(testf, "pkg", repo, "DOMAINS")
    assert "rmod" in got


def test_relative_from_star_expansion_custom_root(tmp_path):
    # Create repo/sub/child.py and a test inside repo/pkg/tests that does 'from ..sub import *'
    repo = tmp_path / "repo"
    sub = repo / "sub"
    sub.mkdir(parents=True)
    child = sub / "child.py"
    child.write_text("DOMAINS = ['child']\n")

    pkg_tests = repo / "pkg" / "tests"
    pkg_tests.mkdir(parents=True)
    testf = pkg_tests / "test_rel_star.py"
    testf.write_text("from ..sub import *\n")

    # Use root_import 'sub' so that expanded candidates 'sub.child' match
    found = find_imports_in_file(testf, "sub", repo)
    assert any(name.startswith("sub.") for name in found)
