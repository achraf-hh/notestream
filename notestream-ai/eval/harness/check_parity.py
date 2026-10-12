"""Check that the eval's ProductionRetriever matches what NoteStream itself retrieves.

Asks a few probe questions through the real API and compares the chunks NoteStream cites
with the eval's ranking for the same question. This calls the LLM (a few cents) and saves
the probe questions in the course's question history.

Usage: python -m eval.harness.check_parity
"""

import sys

import httpx

from eval.corpus.state import paper_by_document_id, require_state
from eval.harness.retrievers import ProductionRetriever
from eval.settings import API_URL

PROBES = (
    "How are failures of worker machines handled?",
    "How does the system decide which replica is the primary?",
    "How are conflicting versions of the same data reconciled?",
)
TOP_K = 5  # the Java API's default rag.retrieval-limit
TOLERANCE = 3  # extra ranks that count as a near miss rather than a failure


def classify(cited: set[int], ranked: list[int]) -> str:
    """Compare the chunks NoteStream cited with the eval's ranking for the same question.

    "inconclusive": nothing was cited, so there is nothing to compare.
    "ok":   every cited chunk is in the eval's top 5.
    "near": every cited chunk is within the top 8. The Java API and the eval embed the question
            in separate calls, and tiny differences can swap chunks that are tied around rank 5.
    "fail": a cited chunk ranks below 8, so the two retrievals really differ.
    """
    if not cited:
        return "inconclusive"
    if cited <= set(ranked[:TOP_K]):
        return "ok"
    if cited <= set(ranked[: TOP_K + TOLERANCE]):
        return "near"
    return "fail"


def main() -> int:
    state = require_state()
    outcomes = []
    with (
        httpx.Client(base_url=API_URL, timeout=120) as api,
        ProductionRetriever(state["course_id"], paper_by_document_id(state)) as retriever,
    ):
        for probe in PROBES:
            response = api.post(
                f"/api/courses/{state['course_id']}/questions", json={"question": probe}
            )
            response.raise_for_status()
            cited = {citation["chunkId"] for citation in response.json()["citations"]}
            ranked = [chunk.chunk_id for chunk in retriever.retrieve(probe, TOP_K + TOLERANCE)]
            outcome = classify(cited, ranked)
            outcomes.append(outcome)
            print(f"{outcome:<12} {probe}\n             cited {sorted(cited)}, eval ranking {ranked}")

    if "fail" in outcomes:
        print("parity FAILED: NoteStream cited chunks the eval ranks below 8")
        return 1
    if set(outcomes) == {"inconclusive"}:
        print("parity not checked: no probe produced citations")
        return 1
    print("parity ok" + (" (with near misses, see above)" if "near" in outcomes else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
