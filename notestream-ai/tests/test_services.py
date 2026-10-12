from types import SimpleNamespace

from app.services.embedding_service import EmbeddingService


class FakeEmbeddingsApi:
    def __init__(self):
        self.calls = []

    def create(self, model, input):
        self.calls.append((model, input))
        return SimpleNamespace(data=[SimpleNamespace(embedding=[float(i)]) for i, _ in enumerate(input)])


def test_embedding_service_returns_vectors_in_input_order():
    api = FakeEmbeddingsApi()
    service = EmbeddingService(SimpleNamespace(embeddings=api), "test-embedding-model")

    assert service.embed(["a", "b", "c"]) == [[0.0], [1.0], [2.0]]
    assert api.calls == [("test-embedding-model", ["a", "b", "c"])]
