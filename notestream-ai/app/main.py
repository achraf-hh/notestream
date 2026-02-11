from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import EmbedRequest, EmbedResponse, AskRequest, AskResponse
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService


# Create FastAPI app
app = FastAPI(
    title="NoteStream AI Service",
    description="Embedding and LLM service for NoteStream RAG pipeline",
    version="1.0.0",
)

# Allow Java backend (port 8080) to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (once, at startup)
embedding_service = EmbeddingService()
llm_service = LLMService()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    """Convert texts to embeddings."""
    try:
        embeddings = embedding_service.embed(request.texts)
        return EmbedResponse(embeddings=embeddings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """Answer a question using provided context chunks."""
    try:
        result = llm_service.ask(request.question, request.context_chunks)
        return AskResponse(answer=result["answer"], citations=result["citations"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)