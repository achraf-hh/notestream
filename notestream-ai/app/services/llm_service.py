from openai import OpenAI

from app.config import settings
from app.utils.citation_parser import parse_citations


class LLMService:
    """Generates answers from questions using context chunks."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
    
    def ask(self, question: str, context_chunks: list[str]) -> dict:
        """
        Answer a question based on provided context chunks.
        
        Args:
            question: The user's question
            context_chunks: Relevant text chunks from the database
            
        Returns:
            {"answer": str, "citations": list[int]}
        """
        # Build the context with numbered chunks
        numbered_context = self._build_context(context_chunks)
        
        # System prompt: instructions for the LLM
        system_prompt = (
            "You are a helpful assistant that answers questions based on the provided context. "
            "Use ONLY the information from the context chunks below. "
            "Always cite your sources using [0], [1], [2] etc. to reference chunk numbers. "
            "If the context doesn't contain enough information, say so."
        )
        
        # User prompt: context + question
        user_prompt = f"""Context:
{numbered_context}

Question: {question}

Answer the question using the context above. Cite sources using [0], [1], etc."""
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        
        # Extract answer text
        answer = response.choices[0].message.content
        
        # Parse citations from the answer
        citations = parse_citations(answer, max_index=len(context_chunks) - 1)
        
        return {
            "answer": answer,
            "citations": citations,
        }
    
    def _build_context(self, chunks: list[str]) -> str:
        """Format chunks with numbers for citation."""
        parts = []
        for i, chunk in enumerate(chunks):
            parts.append(f"[{i}]: {chunk}")
        return "\n\n".join(parts)