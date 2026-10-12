"""Where the eval scripts find the running NoteStream stack and their files.

Defaults match `docker compose up` on this machine. Override them with environment variables.
"""

import os
from pathlib import Path

API_URL = os.environ.get("NOTESTREAM_API_URL", "http://localhost:8080")
AI_URL = os.environ.get("NOTESTREAM_AI_URL", "http://localhost:8000")
DATABASE_URL = os.environ.get(
    "NOTESTREAM_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/notestream"
)

EVAL_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = EVAL_DIR / "corpus" / "manifest.yaml"
DATASET_PATH = EVAL_DIR / "datasets" / "distributed-systems" / "questions.yaml"
RESULTS_DIR = EVAL_DIR / "results"

# Local only (gitignored): downloaded PDFs, ingest state, exported chunks, miss reports.
DATA_DIR = EVAL_DIR / "data"
PAPERS_DIR = DATA_DIR / "papers"
STATE_PATH = DATA_DIR / "state.json"
CHUNKS_PATH = DATA_DIR / "chunks.jsonl"
REPORTS_DIR = DATA_DIR / "reports"
