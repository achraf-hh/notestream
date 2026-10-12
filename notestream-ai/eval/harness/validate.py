"""Check questions.yaml.

Schema checks always run. Without --schema-only, each evidence phrase is also checked
against the exported chunks with your matching.contains(): a phrase must be found in its
own paper, and a phrase also found in another paper is reported as not distinctive.

Usage: python -m eval.harness.validate [--schema-only]
"""

import argparse
import sys
from collections import Counter

from eval.corpus.chunks import load_chunks
from eval.corpus.manifest import load_manifest
from eval.harness import matching
from eval.harness.dataset import check_schema, parse_questions, read_dataset
from eval.settings import DATASET_PATH


def check_evidence(questions, chunks) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    for question in questions:
        for phrase in question.evidence:
            found_in = {chunk.paper for chunk in chunks if matching.contains(chunk.content, phrase)}
            if question.paper not in found_in:
                errors.append(f"{question.id}: phrase not found in {question.paper}: {phrase!r}")
            elif found_in - {question.paper}:
                others = ", ".join(sorted(found_in - {question.paper}))
                warnings.append(f"{question.id}: phrase also appears in {others}: {phrase!r}")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--schema-only", action="store_true", help="skip the checks against chunks")
    args = parser.parse_args()

    manifest = load_manifest()
    raw = read_dataset(DATASET_PATH)
    errors = check_schema(raw, manifest.paper_ids())
    warnings: list[str] = []

    if not errors:
        questions = parse_questions(raw)
        counts = Counter(question.category for question in questions)
        summary = ", ".join(f"{count} {category}" for category, count in counts.items())
        print(f"{len(questions)} questions ({summary or 'none yet'})")

        if not args.schema_only:
            try:
                evidence_errors, warnings = check_evidence(
                    [q for q in questions if q.answerable], load_chunks()
                )
                errors.extend(evidence_errors)
            except NotImplementedError as missing:
                print(f"skipped the evidence checks: {missing}")

    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}")
    print("ok" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
