from pathlib import Path

from splurge_test_namer.namer import build_proposals


def test_build_proposals_respects_excludes(tmp_path: Path) -> None:
    """build_proposals should not include files under excluded subfolders.

    We create a small tests/ tree with an included and an excluded folder, each
    containing a test_*.py file with a DOMAINS sentinel. When calling
    build_proposals with the excluded folder name, proposals must not contain
    origins from that folder.
    """
    root = tmp_path / "tests"
    included = root / "included"
    excluded = root / "excluded_dir"
    included.mkdir(parents=True)
    excluded.mkdir(parents=True)

    incl_file = included / "test_included.py"
    excl_file = excluded / "test_excluded.py"

    # simple sentinel declarations
    incl_file.write_text("DOMAINS = ['INCLUDED']\n")
    excl_file.write_text("DOMAINS = ['EXCLUDED']\n")

    proposals = build_proposals(root, "DOMAINS", excludes=["excluded_dir"])

    # ensure we have at least one proposal (the included file)
    assert any(p[0].name == "test_included.py" for p in proposals)

    # ensure none of the proposals originate from the excluded directory
    assert not any("excluded_dir" in (str(p[0].parts)) for p in proposals)
