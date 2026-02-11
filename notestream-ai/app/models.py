from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    """POST /embed - Input"""
    texts: list[str]


class EmbedResponse(BaseModel):
    """POST /embed - Output"""
    embeddings: list[list[float]]


class AskRequest(BaseModel):
    """POST /ask - Input"""
    question: str
    context_chunks: list[str] = Field(alias="contextChunks")

    class Config:
        populate_by_name = True


class AskResponse(BaseModel):
    """POST /ask - Output"""
    answer: str
    citations: list[int]