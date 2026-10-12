from eval.harness.report import QuestionScore, summarize


def test_summary_groups_by_category():
    scores = [
        QuestionScore("q1", "wording", hit=1.0, reciprocal_rank=1.0),
        QuestionScore("q2", "wording", hit=0.0, reciprocal_rank=0.0),
        QuestionScore("q3", "paraphrase", hit=1.0, reciprocal_rank=0.5),
    ]

    summary = summarize(scores)

    assert list(summary) == ["all", "wording", "paraphrase"]
    assert summary["all"] == {"count": 3, "hits": 2.0, "hit_rate": 2 / 3, "mrr": 0.5}
    assert summary["wording"]["hit_rate"] == 0.5
    assert summary["paraphrase"]["mrr"] == 0.5


def test_summary_of_no_scores():
    assert summarize([]) == {"all": {"count": 0, "hits": 0, "hit_rate": 0.0, "mrr": 0.0}}
