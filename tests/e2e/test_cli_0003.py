import os
import sys
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
    except Exception as e:
        # Return non-zero code and include exception text for assertions
        return 1, buf.getvalue(), str(e)
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout
        os.chdir(old_cwd)


def test_prefix_and_fallback(tmp_path):
    repo = tmp_path / "repo"
    tests = repo / "tests"
    tests.mkdir(parents=True)

    a = tests / "test_a.py"
    b = tests / "test_b.py"
    # one file has no sentinel -> fallback should be used
    a.write_text("# no sentinel here\n")
    # one file has sentinel with spaces and mixed case
    b.write_text("DOMAINS = ['Alpha Beta']\n")

    # Dry-run with custom prefix and fallback
    code, out, err = run_cli(["--test-root", str(tests), "--prefix", "SpecTest", "--fallback", "MyFallback"], cwd=repo)
    assert code == 0
    assert "DRY RUN" in out
    # Ensure fallback and prefix appear in dry-run output
    assert "SpecTest_MyFallback" in out or "SpecTest_Alpha_Beta" in out

    # Apply renames
    code2, out2, err2 = run_cli(
        ["--test-root", str(tests), "--prefix", "SpecTest", "--fallback", "MyFallback", "--apply", "--force"], cwd=repo
    )
    assert code2 == 0
    names = [p.name for p in tests.iterdir()]
    assert any(n.startswith("SpecTest_") for n in names)
