from splurge_test_namer.namer import slug_sentinel_list


def test_slug_replaces_spaces_and_dashes():
    vals = ["Alpha Beta", "gamma-delta", "OK"]
    slug = slug_sentinel_list(vals)
    # spaces and dashes become underscores, lowercased
    assert slug == "alpha_beta_gamma_delta_ok"


def test_slug_trims_repeats_and_empty_parts():
    vals = ["  ", "--a--", "b  c"]
    slug = slug_sentinel_list(vals)
    assert slug == "a_b_c"
