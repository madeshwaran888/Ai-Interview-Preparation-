from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP
def chunk_text(text: str) -> list[str]:
    """
    Split a document into overlapping chunks.
    Strategy — RecursiveCharacterTextSplitter tries
    separators in order until chunks fit the size budget:
      1. Paragraph breaks  (\n\n)
      2. Line breaks       (\n)
      3. Sentence ends     (.)
      4. Word boundaries   ( )
    Args:
        text: Raw document string.
    Returns:
        List of chunk strings, each ≤ CHUNK_SIZE characters
        with CHUNK_OVERLAP characters of context from the
        previous chunk."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    # Remove empty / whitespace-only chunks
    return [c.strip() for c in chunks if c.strip()]

if __name__ == "__main__":
    sample = (
        "What is a Python generator?\n\n"
        "A generator is a function that uses the yield keyword to return "
        "values one at a time, pausing execution between each call. "
        "They are memory-efficient because they produce items lazily.\n\n"
        "Example:\n\ndef count_up(n):\n    for i in range(n):\n        yield i"
    )
    result = chunk_text(sample)
    print(f"Chunks produced: {len(result)}")
    for i, c in enumerate(result, 1):
        print(f"\n--- Chunk {i} ({len(c)} chars) ---\n{c}")
