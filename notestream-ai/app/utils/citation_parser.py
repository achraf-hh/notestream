import re


def parse_citations(text: str, max_index: int) -> list[int]:
    """
    Extract citation indices from LLM response text.
    
    Recognizes patterns like:
    - [0], [1], [2]
    - chunk 0, chunk 1
    - chunks 0, 2, and 4
    - (chunk 3)
    
    Args:
        text: The LLM's response text
        max_index: Highest valid chunk index (for filtering bad values)
    
    Returns:
        Sorted, deduplicated list of valid citation indices.
        Returns [0] if no citations found (fallback).
    """
    indices = set()
    
    # Pattern 1: [0], [1], [12]
    bracket_pattern = r'\[(\d+)\]'
    for match in re.finditer(bracket_pattern, text):
        indices.add(int(match.group(1)))
    
    # Pattern 2: "chunk 0", "chunk 12", "Chunk 3"
    chunk_pattern = r'[Cc]hunk\s*(\d+)'
    for match in re.finditer(chunk_pattern, text):
        indices.add(int(match.group(1)))
    
    # Filter: keep only valid indices (0 to max_index)
    valid_indices = [i for i in indices if 0 <= i <= max_index]
    
    # Fallback: if nothing found, assume first chunk
    if not valid_indices:
        return [0]
    
    return sorted(valid_indices)