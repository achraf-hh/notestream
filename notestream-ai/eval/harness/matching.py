"""Decides whether a chunk contains an evidence phrase. Yours to write (PLAN.md, M1).

Write tests/eval/test_matching.py first, using real strings from eval/data/chunks.jsonl
and phrases copied from the PDFs. The validator and the eval runner both call these two
functions, so there is only one definition of "this chunk contains the evidence".
"""


def normalize(text: str) -> str:
    """Return a canonical form of `text`, so the same sentence from a PDF viewer and from
    NoteStream's chunks compares equal."""
    raise NotImplementedError("normalize() is yours to write: see PLAN.md, M1")


def contains(chunk: str, phrase: str) -> bool:
    """Return True if `phrase` appears in `chunk` once both are normalized."""
    raise NotImplementedError("contains() is yours to write: see PLAN.md, M1")
