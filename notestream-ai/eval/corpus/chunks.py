import json
from dataclasses import dataclass

from eval.settings import CHUNKS_PATH


@dataclass(frozen=True)
class Chunk:
    chunk_id: int
    paper: str
    chunk_index: int
    content: str


def load_chunks(path=CHUNKS_PATH) -> list[Chunk]:
    if not path.exists():
        raise SystemExit(f"{path} not found. Run: python -m eval.corpus.export_chunks")
    with path.open() as lines:
        return [Chunk(**json.loads(line)) for line in lines if line.strip()]
