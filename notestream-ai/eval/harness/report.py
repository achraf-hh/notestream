"""Aggregate per-question scores into the summary table the runner prints and saves."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QuestionScore:
    question_id: str
    category: str
    hit: float
    reciprocal_rank: float


def summarize(scores: list[QuestionScore]) -> dict[str, dict]:
    """Group scores into "all" plus one group per category, in first-seen order."""
    groups: dict[str, list[QuestionScore]] = {"all": list(scores)}
    for score in scores:
        groups.setdefault(score.category, []).append(score)

    summary = {}
    for name, members in groups.items():
        count = len(members)
        hits = sum(member.hit for member in members)
        summary[name] = {
            "count": count,
            "hits": hits,
            "hit_rate": hits / count if count else 0.0,
            "mrr": sum(member.reciprocal_rank for member in members) / count if count else 0.0,
        }
    return summary


def format_summary(summary: dict[str, dict], k: int) -> str:
    lines = [f"{'group':<12} {'questions':>9} {f'hit@{k}':>12} {f'MRR@{k}':>8}"]
    for name, row in summary.items():
        hits = f"{row['hits']:g}/{row['count']} ({row['hit_rate']:.0%})"
        lines.append(f"{name:<12} {row['count']:>9} {hits:>12} {row['mrr']:>8.3f}")
    return "\n".join(lines)
