"""Load and check the golden dataset (questions.yaml)."""

from dataclasses import dataclass

import yaml

CATEGORIES = ("wording", "paraphrase", "unanswerable")
ALLOWED_FIELDS = {"id", "paper", "category", "question", "evidence", "notes"}

# NoteStream's chunks overlap by 50 characters, so a phrase this short always sits whole
# inside at least one chunk. Longer phrases can be split across two chunks and never match.
MAX_PHRASE_LENGTH = 45


@dataclass(frozen=True)
class Question:
    id: str
    question: str
    category: str
    paper: str | None
    evidence: tuple[str, ...]

    @property
    def answerable(self) -> bool:
        return self.category != "unanswerable"


def read_dataset(path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def check_schema(raw: dict, paper_ids: set[str]) -> list[str]:
    """Return every problem found in the parsed YAML. An empty list means the file is valid."""
    if not isinstance(raw, dict) or "version" not in raw or "questions" not in raw:
        return ["the file needs top-level `version` and `questions` keys"]
    if not isinstance(raw["questions"], list):
        return ["`questions` must be a list"]

    problems = []
    seen_ids = set()
    for position, item in enumerate(raw["questions"], start=1):
        if not isinstance(item, dict):
            problems.append(f"entry {position}: must be a mapping with id, category, question, ...")
            continue
        label = item.get("id") or f"entry {position}"

        unknown = set(item) - ALLOWED_FIELDS
        if unknown:
            problems.append(f"{label}: unknown field(s) {sorted(unknown)}")

        question_id = item.get("id")
        if not isinstance(question_id, str) or not question_id:
            problems.append(f"{label}: needs an `id`")
        elif question_id in seen_ids:
            problems.append(f"{label}: duplicate id")
        seen_ids.add(question_id)

        if not isinstance(item.get("question"), str) or not item["question"].strip():
            problems.append(f"{label}: needs a `question`")

        category = item.get("category")
        if category not in CATEGORIES:
            problems.append(f"{label}: `category` must be one of {', '.join(CATEGORIES)}")
            continue

        paper = item.get("paper")
        evidence = item.get("evidence") or []
        if paper is not None and paper not in paper_ids:
            problems.append(f"{label}: `paper` must be one of {', '.join(sorted(paper_ids))}")

        if category == "unanswerable":
            if evidence:
                problems.append(f"{label}: unanswerable questions have no `evidence`")
            continue

        if paper is None:
            problems.append(f"{label}: answerable questions need a `paper`")
        if not isinstance(evidence, list) or not evidence:
            problems.append(f"{label}: needs at least one `evidence` phrase")
            continue
        for phrase in evidence:
            if not isinstance(phrase, str) or not phrase.strip():
                problems.append(f"{label}: evidence phrases must be non-empty text")
            elif len(phrase) > MAX_PHRASE_LENGTH:
                problems.append(
                    f"{label}: evidence phrase is {len(phrase)} characters, max is "
                    f"{MAX_PHRASE_LENGTH}: {phrase!r}"
                )

    return problems


def parse_questions(raw: dict) -> list[Question]:
    """Build Question objects from YAML that already passed check_schema."""
    return [
        Question(
            id=item["id"],
            question=item["question"].strip(),
            category=item["category"],
            paper=item.get("paper"),
            evidence=tuple(item.get("evidence") or ()),
        )
        for item in raw["questions"]
    ]
