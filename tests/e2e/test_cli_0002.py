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
        return 1, buf.getvalue(), str(e)
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout
        os.chdir(old_cwd)


def test_long_tokens_trigger_validation(tmp_path):
    repo = tmp_path / "repo_long"
    tests = repo / "tests"
    tests.mkdir(parents=True)

    # Create a file with a long token that will sanitize to >64 chars
    long_token = "X" * 80
    a = tests / "test_long.py"
    a.write_text(f"DOMAINS = ['{long_token}']\n")

    # Dry-run should fail when sanitization makes token too long; CLI will
    # return a non-zero code and include the error text in stderr or stdout.
    code, out, err = run_cli(["--test-root", str(tests)], cwd=repo)
    assert code != 0
    assert ("too long" in (err or out).lower()) or ("sentinel" in (err or out).lower())
