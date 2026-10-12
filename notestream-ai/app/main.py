from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies import get_embedding_service, get_llm_service
from app.models import AskRequest, AskResponse, EmbedRequest, EmbedResponse
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail fast at startup when OPENAI_API_KEY is missing. Settings load lazily,
    # so importing the app (e.g. in tests) doesn't need a key.
    get_settings()
    yield


# Create FastAPI app
app = FastAPI(
    title="NoteStream AI Service",
    description="Embedding and LLM service for NoteStream RAG pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow Java backend (port 8080) to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/embed", response_model=EmbedResponse)
def embed(
    request: EmbedRequest,
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
):
    """Convert texts to embeddings."""
    try:
        embeddings = embedding_service.embed(request.texts)
        return EmbedResponse(embeddings=embeddings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    llm_service: Annotated[LLMService, Depends(get_llm_service)],
):
    """Answer a question using provided context chunks."""
    try:
        result = llm_service.ask(request.question, request.context_chunks)
        return AskResponse(answer=result["answer"], citations=result["citations"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
