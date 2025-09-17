import os
import sys
import importlib


def run_main_with_args(args, cwd):
    """Run cli.main() with given argv and cwd, return (exit_code, out, err)."""
    old_argv = sys.argv[:]
    old_cwd = os.getcwd()
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    try:
        os.chdir(str(cwd))
        sys.argv = ["splurge_test_namer"] + args
        import splurge_test_namer.cli as cli

        importlib.reload(cli)
        try:
            cli.main()
            return 0
        except SystemExit as e:
            return e.code if isinstance(e.code, int) else 1
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)
        sys.stdout = old_stdout


def test_invalid_sentinel_name(tmp_path):
    tests = tmp_path / "tests"
    tests.mkdir()
    # empty sentinel should cause SystemExit(2)
    code = run_main_with_args(["--test-root", str(tests), "--sentinel", ""], cwd=tmp_path)
    assert code == 2


def test_invalid_root_import_format(tmp_path):
    tests = tmp_path / "tests"
    tests.mkdir()
    # invalid dotted import should cause exit
    code = run_main_with_args(["--test-root", str(tests), "--import-root", "bad..name"], cwd=tmp_path)
    assert code == 2


def test_invalid_repo_root(tmp_path):
    # repo-root that doesn't exist should cause exit
    tests = tmp_path / "tests"
    tests.mkdir()
    code = run_main_with_args(["--test-root", str(tests), "--repo-root", str(tmp_path / "nope")], cwd=tmp_path)
    assert code == 2


def test_fallback_normalization_and_invalid(tmp_path):
    tests = tmp_path / "tests"
    tests.mkdir()
    # fallback with illegal characters will normalize; if it begins with digit after normalize, it's invalid
    code = run_main_with_args(["--test-root", str(tests), "--fallback", "1BAD"], cwd=tmp_path)
    assert code == 2


def test_invalid_prefix(tmp_path):
    tests = tmp_path / "tests"
    tests.mkdir()
    code = run_main_with_args(["--test-root", str(tests), "--prefix", "1badprefix"], cwd=tmp_path)
    assert code == 2


def test_dry_run_happy_path(tmp_path):
    # create a simple test file with DOMAINS sentinel so build_proposals finds something
    repo = tmp_path
    tests = repo / "tests"
    tests.mkdir()
    f = tests / "test_one.py"
    f.write_text("DOMAINS = ['alpha']\n")
    code = run_main_with_args(["--test-root", str(tests)], cwd=repo)
    # main should return 0 for dry-run
    assert code == 0
