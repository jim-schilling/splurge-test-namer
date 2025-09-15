from pathlib import Path

import pytest

from splurge_test_namer.namer import build_proposals, apply_renames


def create_test_file(p: Path, sentinel_name: str, domains: list[str]):
    p.parent.mkdir(parents=True, exist_ok=True)
    content = f"\n# sentinel {sentinel_name}\n{sentinel_name} = {domains!r}\n"
    p.write_text(content)


def test_integration_rename_flow(tmp_path):
    tests_root = tmp_path / "tests"
    # Create two test files that share the same sentinel so they'll be grouped
    a = tests_root / "test_alpha.py"
    b = tests_root / "test_bravo.py"
    create_test_file(a, "DOMAINS", ["alpha"])
    create_test_file(b, "DOMAINS", ["alpha"])

    proposals = build_proposals(tests_root, "DOMAINS")
    # Expect two proposals
    assert len(proposals) == 2

    # Simulate existing targets by creating files at proposed destinations
    for _, dst in proposals:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text("# colliding")

    # Running apply_renames without force should raise an error due to collision
    with pytest.raises(Exception):
        apply_renames(proposals, force=False)

    # With force, it should succeed (overwrite existing targets)
    apply_renames(proposals, force=True)

    # Ensure targets exist and origins no longer exist
    for orig, dst in proposals:
        assert dst.exists()
        assert not orig.exists()
