"""API tests for the AI service. OpenAI is never called: the services are replaced with fakes."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_embedding_service, get_llm_service
from app.main import app

SERVICE_ROOT = Path(__file__).resolve().parent.parent


class FakeEmbeddingService:
    def __init__(self):
        self.calls = []

    def embed(self, texts):
        self.calls.append(texts)
        return [[float(i), 0.5] for i, _ in enumerate(texts)]


class FakeLLMService:
    def __init__(self):
        self.calls = []

    def ask(self, question, context_chunks):
        self.calls.append((question, context_chunks))
        return {"answer": "The second chunk answers it [1].", "citations": [1]}


class FailingEmbeddingService:
    def embed(self, texts):
        raise RuntimeError("upstream failure")


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


def use(dependency, fake):
    app.dependency_overrides[dependency] = lambda: fake
    return fake


def test_app_imports_without_openai_key(tmp_path):
    env = {key: value for key, value in os.environ.items() if key != "OPENAI_API_KEY"}
    env["PYTHONPATH"] = str(SERVICE_ROOT)

    # Run from an empty directory so no .env file can supply the key either.
    result = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_embed_returns_one_embedding_per_text(client):
    fake = use(get_embedding_service, FakeEmbeddingService())

    response = client.post("/embed", json={"texts": ["first", "second"]})

    assert response.status_code == 200
    assert response.json() == {"embeddings": [[0.0, 0.5], [1.0, 0.5]]}
    assert fake.calls == [["first", "second"]]


def test_embed_returns_500_when_the_service_fails(client):
    use(get_embedding_service, FailingEmbeddingService())

    response = client.post("/embed", json={"texts": ["first"]})

    assert response.status_code == 500


def test_ask_accepts_the_field_names_the_java_api_sends(client):
    fake = use(get_llm_service, FakeLLMService())

    response = client.post(
        "/ask",
        json={"question": "Which chunk answers it?", "contextChunks": ["chunk zero", "chunk one"]},
    )

    assert response.status_code == 200
    assert response.json() == {"answer": "The second chunk answers it [1].", "citations": [1]}
    assert fake.calls == [("Which chunk answers it?", ["chunk zero", "chunk one"])]
