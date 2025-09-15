import sys
import os
import io
import importlib


def run_cli(args, cwd):
    """Run the CLI by calling main() directly.

    Returns: (exit_code, stdout, stderr)
    """
    # prepare environment
    old_cwd = os.getcwd()
    old_argv = sys.argv[:]
    old_stdout = sys.stdout
    buf = io.StringIO()
    try:
        os.chdir(str(cwd))
        sys.argv = ["splurge_test_namer"] + args
        # import and reload to ensure fresh module state in tests
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


def test_e2e_cli_dry_and_apply(tmp_path):
    # Prepare a small repo with test files
    repo = tmp_path / "repo"
    tests = repo / "tests"
    tests.mkdir(parents=True)

    a = tests / "test_one.py"
    b = tests / "test_two.py"
    a.write_text("DOMAINS = ['alpha']\n")
    b.write_text("DOMAINS = ['alpha']\n")

    # Dry-run: expect proposals printed
    code, out, err = run_cli(["--root", str(tests), "--repo-root", str(repo)], cwd=repo)
    assert code == 0
    assert "DRY RUN" in out

    # Apply with force
    code2, out2, err2 = run_cli(["--root", str(tests), "--repo-root", str(repo), "--apply", "--force"], cwd=repo)
    assert code2 == 0

    # verify that target files exist and original files no longer exist
    names = [p.name for p in tests.iterdir()]
    assert any(n.startswith("test_alpha_") for n in names)
