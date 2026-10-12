"""Ingest state: which course the corpus lives in and which NoteStream document holds each paper."""

import json

from eval.settings import STATE_PATH


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text())


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def require_state() -> dict:
    state = load_state()
    if not state.get("documents"):
        raise SystemExit("No ingested corpus yet. Run: python -m eval.corpus.ingest")
    return state


def corpus_mismatch(state: dict, manifest_version: str) -> str | None:
    """Explain why the ingested course doesn't match the manifest, or return None if it does."""
    ingested = state.get("corpus_version")
    if ingested is None or ingested == manifest_version:
        return None
    return (
        f"The course in {STATE_PATH.name} holds corpus {ingested}, but manifest.yaml is "
        f"{manifest_version}. Mixing versions in one course would mislabel every result. "
        f"Move {STATE_PATH.name} aside to ingest into a fresh course."
    )


def paper_by_document_id(state: dict) -> dict[int, str]:
    return {document_id: paper_id for paper_id, document_id in state["documents"].items()}
