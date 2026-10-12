"""Retrievers the eval can run. M1 has one: NoteStream's production retrieval."""

import json
from dataclasses import dataclass

import httpx
import psycopg

from eval.settings import AI_URL, DATABASE_URL

# Same query as ChunkRepository.findSimilarChunks in the Java API, plus the distance so the
# miss report can show how close each chunk was.
SIMILAR_CHUNKS_SQL = """
    SELECT c.id, c.document_id, c.chunk_index, c.content,
           c.embedding <=> CAST(%(embedding)s AS vector) AS distance
    FROM chunks c
    JOIN documents d ON c.document_id = d.id
    WHERE d.course_id = %(course_id)s
      AND c.embedding IS NOT NULL
    ORDER BY c.embedding <=> CAST(%(embedding)s AS vector)
    LIMIT %(limit)s
"""


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    paper: str
    chunk_index: int
    content: str
    distance: float


class ProductionRetriever:
    """Reproduces NoteStream's retrieval: embed the question through the AI service, then run
    the Java API's pgvector query (cosine distance, filtered to the course)."""

    def __init__(self, course_id: int, paper_by_document_id: dict[int, str]):
        self.course_id = course_id
        self.paper_by_document_id = paper_by_document_id
        self.http = httpx.Client(base_url=AI_URL, timeout=60)
        self.connection = psycopg.connect(DATABASE_URL)

    def retrieve(self, question: str, k: int) -> list[RetrievedChunk]:
        # The Java API trims the question before embedding it.
        response = self.http.post("/embed", json={"texts": [question.strip()]})
        response.raise_for_status()
        embedding = response.json()["embeddings"][0]

        rows = self.connection.execute(
            SIMILAR_CHUNKS_SQL,
            {"embedding": json.dumps(embedding), "course_id": self.course_id, "limit": k},
        ).fetchall()
        return [
            RetrievedChunk(
                chunk_id=chunk_id,
                paper=self.paper_by_document_id.get(document_id, f"document-{document_id}"),
                chunk_index=chunk_index,
                content=content,
                distance=float(distance),
            )
            for chunk_id, document_id, chunk_index, content, distance in rows
        ]

    def close(self) -> None:
        self.http.close()
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()
