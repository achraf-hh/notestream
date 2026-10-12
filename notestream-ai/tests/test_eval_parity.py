from eval.harness.check_parity import classify

RANKED = [10, 11, 12, 13, 14, 15, 16, 17]  # chunk ids, best first


def test_no_citations_is_inconclusive_not_ok():
    assert classify(set(), RANKED) == "inconclusive"


def test_citations_in_the_top_five_are_ok():
    assert classify({10, 14}, RANKED) == "ok"


def test_a_citation_ranked_sixth_to_eighth_is_a_near_miss():
    assert classify({10, 16}, RANKED) == "near"


def test_a_citation_outside_the_top_eight_fails():
    assert classify({10, 99}, RANKED) == "fail"
