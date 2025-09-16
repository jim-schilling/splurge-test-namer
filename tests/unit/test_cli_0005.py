import sys
import os
import io
import importlib


def run_cli(args, cwd):
    old_cwd = os.getcwd()
    old_argv = sys.argv[:]
    old_stdout = sys.stdout
    buf = io.StringIO()
    try:
        os.chdir(str(cwd))
        sys.argv = ["splurge_test_namer"] + args
        import splurge_test_namer.cli as cli

        importlib.reload(cli)
        sys.stdout = buf
        cli.main()
        return 0, buf.getvalue(), ""
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        return code, buf.getvalue(), ""
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout
        os.chdir(old_cwd)


def test_cli_accepts_empty_root_import(tmp_path):
    repo = tmp_path / "repo"
    tests = repo / "tests"
    tests.mkdir(parents=True)
    f = tests / "test_one.py"
    f.write_text("DOMAINS = ['alpha']\n")

    # Pass an explicit empty string for --import-root; CLI should normalize it to None
    code, out, err = run_cli(["--test-root", str(tests), "--repo-root", str(repo), "--import-root", ""], cwd=repo)
    assert code == 0
    assert "DRY RUN" in out
