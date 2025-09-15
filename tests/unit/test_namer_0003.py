
from splurge_test_namer.namer import slug_sentinel_list, build_proposals


def test_slug_sentinel_list_various():
    assert slug_sentinel_list(["Core", "SQL-Utils"]) == "core_sql_utils"
    assert slug_sentinel_list(["__weird__", "--name--"]) == "weird_name"
    assert slug_sentinel_list([]) == "misc"


def test_build_proposals_groups_and_sequencing(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    a = tests_dir / "test_a.py"
    b = tests_dir / "test_b.py"
    c = tests_dir / "test_c.py"
    # two files with same domain, one with another
    a.write_text("DOMAINS = ['alpha']\n")
    b.write_text("DOMAINS = ['alpha']\n")
    c.write_text("DOMAINS = ['beta']\n")

    proposals = build_proposals(tests_dir, "DOMAINS")
    # should produce three proposals
    assert len(proposals) == 3
    # group prefixes
    names = [p.name for _, p in proposals]
    assert any(n.startswith("test_alpha_") for n in names)
    assert any(n.startswith("test_beta_") for n in names)
    # alpha group should have two sequential numbers 0001 and 0002
    alpha_names = sorted([n for n in names if n.startswith("test_alpha_")])
    assert alpha_names[0].endswith("0001.py")
    assert alpha_names[1].endswith("0002.py")
