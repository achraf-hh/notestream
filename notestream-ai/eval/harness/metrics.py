"""Retrieval metrics. Yours to write (PLAN.md, M1).

Write tests/eval/test_metrics.py first, with small examples you worked out on paper.
`relevant` lists the retrieved chunks in rank order: relevant[0] is True when the
top-ranked chunk contains the evidence.
"""


def hit_at_k(relevant: list[bool], k: int) -> float:
    """1.0 if any of the first k results is relevant, else 0.0."""
    raise NotImplementedError("hit_at_k() is yours to write: see PLAN.md, M1")


def mrr_at_k(relevant: list[bool], k: int) -> float:
    """1 / rank of the first relevant result within the first k, or 0.0 if there is none."""
    raise NotImplementedError("mrr_at_k() is yours to write: see PLAN.md, M1")
