"""Export the chunks NoteStream stored for the corpus, one JSON object per line.

Each line: {"chunk_id", "paper", "chunk_index", "content"}. The output (eval/data/chunks.jsonl)
feeds your matching work and the dataset validator.

Usage: python -m eval.corpus.export_chunks
"""

import json
import sys

import psycopg

from eval.corpus.state import paper_by_document_id, require_state
from eval.settings import CHUNKS_PATH, DATABASE_URL

CHUNKS_SQL = """
    SELECT id, document_id, chunk_index, content
    FROM chunks
    WHERE document_id = ANY(%(document_ids)s)
    ORDER BY document_id, chunk_index
"""


def main() -> int:
    state = require_state()
    papers = paper_by_document_id(state)

    with psycopg.connect(DATABASE_URL) as connection:
        rows = connection.execute(CHUNKS_SQL, {"document_ids": list(papers)}).fetchall()

    CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHUNKS_PATH.open("w") as output:
        for chunk_id, document_id, chunk_index, content in rows:
            line = {
                "chunk_id": chunk_id,
                "paper": papers[document_id],
                "chunk_index": chunk_index,
                "content": content,
            }
            output.write(json.dumps(line) + "\n")

    counts = {paper: 0 for paper in papers.values()}
    for row in rows:
        counts[papers[row[1]]] += 1
    print(f"exported {len(rows)} chunks to {CHUNKS_PATH}")
    for paper, count in counts.items():
        print(f"  {paper:<10} {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
