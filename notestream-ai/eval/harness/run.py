"""Run the M1 retrieval baseline: production top-k retrieval for every question in the dataset.

Prints hit@k and MRR@k overall and per category, and saves the run to eval/results/
(ids and scores only, no paper text). Also writes a miss report with the retrieved text
to eval/data/reports/ (gitignored) so you can read every miss.

Usage: python -m eval.harness.run [--k 5] [--label baseline]
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime

from eval.corpus.manifest import load_manifest
from eval.corpus.state import corpus_mismatch, paper_by_document_id, require_state
from eval.harness import matching, metrics
from eval.harness.dataset import check_schema, parse_questions, read_dataset
from eval.harness.report import QuestionScore, format_summary, summarize
from eval.harness.retrievers import ProductionRetriever
from eval.settings import DATASET_PATH, REPORTS_DIR, RESULTS_DIR


def git_info() -> dict:
    def git(*args):
        return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()

    return {"git_commit": git("rev-parse", "HEAD"), "git_dirty": bool(git("status", "--porcelain"))}


def score(question, retrieved, k) -> tuple[list[bool], QuestionScore]:
    relevant = [
        any(matching.contains(chunk.content, phrase) for phrase in question.evidence)
        for chunk in retrieved
    ]
    return relevant, QuestionScore(
        question_id=question.id,
        category=question.category,
        hit=metrics.hit_at_k(relevant, k),
        reciprocal_rank=metrics.mrr_at_k(relevant, k),
    )


def write_report(path, k, rows) -> None:
    lines = [f"# Misses and unanswerable questions (top {k})", ""]
    for question, retrieved, relevant in rows:
        if question.answerable and any(relevant):
            continue
        lines += [f"## {question.id} ({question.category}) {question.question}", ""]
        if question.evidence:
            lines += [f"Expected in **{question.paper}**: " + "; ".join(question.evidence), ""]
        for rank, chunk in enumerate(retrieved, start=1):
            text = " ".join(chunk.content.split())[:400]
            lines += [
                f"{rank}. **{chunk.paper}** chunk {chunk.chunk_index}, distance {chunk.distance:.3f}",
                f"   > {text}",
            ]
        lines.append("")
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--label", default="baseline")
    args = parser.parse_args()

    manifest = load_manifest()
    state = require_state()
    raw = read_dataset(DATASET_PATH)
    problems = check_schema(raw, manifest.paper_ids())
    if problems:
        print("questions.yaml has problems. Run: python -m eval.harness.validate")
        return 1
    mismatch = corpus_mismatch(state, manifest.version)
    if mismatch:
        print(f"warning: {mismatch}\n")
    questions = parse_questions(raw)
    if not any(question.answerable for question in questions):
        print("No answerable questions yet. Add some to questions.yaml first.")
        return 1

    rows, scores = [], []
    try:
        with ProductionRetriever(state["course_id"], paper_by_document_id(state)) as retriever:
            for question in questions:
                retrieved = retriever.retrieve(question.question, args.k)
                relevant = [False] * len(retrieved)
                if question.answerable:
                    relevant, question_score = score(question, retrieved, args.k)
                    scores.append(question_score)
                rows.append((question, retrieved, relevant))
    except NotImplementedError as missing:
        print(f"Can't score yet: {missing}")
        return 1

    summary = summarize(scores)
    print(format_summary(summary, args.k))

    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    run = {
        "label": args.label,
        "created_at": timestamp,
        **git_info(),
        "k": args.k,
        "dataset_version": raw["version"],
        "corpus_version": state.get("corpus_version"),
        "summary": summary,
        "questions": [
            {
                "id": question.id,
                "category": question.category,
                "paper": question.paper,
                "retrieved": [
                    {
                        "chunk_id": chunk.chunk_id,
                        "paper": chunk.paper,
                        "chunk_index": chunk.chunk_index,
                        "distance": round(chunk.distance, 4),
                        "relevant": is_relevant,
                    }
                    for chunk, is_relevant in zip(retrieved, relevant, strict=True)
                ],
            }
            for question, retrieved, relevant in rows
        ],
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS_DIR / f"{timestamp}-{args.label}.json"
    report_path = REPORTS_DIR / f"{timestamp}-{args.label}-misses.md"
    result_path.write_text(json.dumps(run, indent=2) + "\n")
    write_report(report_path, args.k, rows)
    print(f"\nsaved {result_path}\nmiss report {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
