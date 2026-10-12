from openai import OpenAI


class EmbeddingService:
    """Converts text into vector embeddings using OpenAI API."""
    
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Convert texts to embeddings.
        
        Args:
            texts: List of strings to embed
            
        Returns:
            List of embeddings (each is 1536 floats for text-embedding-3-small)
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        
        # Extract embeddings in same order as input
        embeddings = [item.embedding for item in response.data]
        
        return embeddings