"""Upload the corpus to NoteStream through its public API, the same path a user takes.

Creates the course on the first run and uploads each paper once. Before uploading, it asks the
server which papers the course already holds: the server is the source of truth, and
eval/data/state.json is only a record of it. Each upload calls OpenAI for embeddings (a few
cents for the whole corpus).

Usage: python -m eval.corpus.ingest
"""

import sys

import httpx

from eval.corpus.manifest import Paper, load_manifest
from eval.corpus.state import corpus_mismatch, load_state, save_state
from eval.settings import API_URL, PAPERS_DIR


def plan_uploads(
    papers: tuple[Paper, ...], on_server: list[dict]
) -> tuple[dict[str, int], list[Paper], list[str]]:
    """Split the manifest into papers the course already holds and papers to upload.

    A paper the server already has is recorded, never uploaded again. That covers an upload
    that finished on the server after the client gave up waiting for the response.
    Returns (paper id -> document id, papers to upload, warnings).
    """
    ids_by_filename: dict[str, list[int]] = {}
    for document in on_server:
        ids_by_filename.setdefault(document["filename"], []).append(document["id"])

    found, missing, warnings = {}, [], []
    for paper in papers:
        ids = sorted(ids_by_filename.get(paper.filename, []))
        if len(ids) > 1:
            warnings.append(
                f"{paper.id}: the course holds {len(ids)} copies (documents {ids}), "
                "so retrieval will return duplicate chunks"
            )
        if ids:
            found[paper.id] = ids[0]
        else:
            missing.append(paper)
    return found, missing, warnings


def main() -> int:
    manifest = load_manifest()
    state = load_state()
    mismatch = corpus_mismatch(state, manifest.version)
    if mismatch:
        print(mismatch)
        return 1

    with httpx.Client(base_url=API_URL, timeout=300) as client:
        try:
            client.get("/health").raise_for_status()
        except httpx.HTTPError as error:
            print(f"NoteStream API not reachable at {API_URL} ({error}). Run: docker compose up -d")
            return 1

        course_id = state.get("course_id")
        if course_id is None or client.get(f"/api/courses/{course_id}").status_code == 404:
            response = client.post(
                "/api/courses",
                json={"name": manifest.course_name, "description": manifest.course_description},
            )
            response.raise_for_status()
            course_id = response.json()["id"]
            state = {"course_id": course_id, "corpus_version": manifest.version, "documents": {}}
            print(f"created course {course_id}: {manifest.course_name}")

        response = client.get(f"/api/courses/{course_id}/documents")
        response.raise_for_status()
        found, missing, warnings = plan_uploads(manifest.papers, response.json())
        for warning in warnings:
            print(f"warning: {warning}")
        state["documents"] = found
        save_state(state)

        for paper in manifest.papers:
            if paper.id in found:
                print(f"ok        {paper.id} (in the course as document {found[paper.id]})")
                continue

            path = PAPERS_DIR / paper.filename
            if not path.exists():
                print(f"missing   {path}. Run: python -m eval.corpus.fetch")
                return 1

            try:
                with path.open("rb") as pdf:
                    response = client.post(
                        f"/api/courses/{course_id}/documents",
                        files={"file": (paper.filename, pdf, "application/pdf")},
                    )
            except httpx.TimeoutException:
                print(f"TIMEOUT   {paper.id}: the server may still have finished the upload.")
                print("          Re-run ingest: it checks the course before uploading again.")
                return 1
            if response.status_code != 201:
                print(f"FAILED    {paper.id}: HTTP {response.status_code} {response.text[:300]}")
                return 1

            state["documents"][paper.id] = response.json()["id"]
            save_state(state)
            print(f"uploaded  {paper.id} as document {state['documents'][paper.id]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
