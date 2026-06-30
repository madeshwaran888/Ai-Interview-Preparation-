import chromadb
from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL, CHROMA_PATH, COLLECTION
_embedder = None
_chroma_client = None

def get_embedder() -> SentenceTransformer:
    """Lazy-load the embedding model (cached after first call)."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder

def get_chroma_client() -> chromadb.PersistentClient:
    """Return a persistent ChromaDB client (cached after first call)."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _chroma_client

def get_or_create_collection() -> chromadb.Collection:
    """Return the ChromaDB collection, creating it if it doesn't exist."""
    client = get_chroma_client()
    try:
        return client.get_collection(COLLECTION)
    except Exception:
        return client.create_collection(COLLECTION)

def embed_and_store(chunks: list[str], source_label: str = "doc") -> int:
    """
    Embed every chunk and add it to ChromaDB.
    Each chunk is stored with:
      - Its dense vector embedding (for similarity search)
      - The raw text            (returned at query time)
      - A source metadata tag   (for filtering / debugging)
    Args:
        chunks       : List of text strings to embed.
        source_label : Tag stored in metadata (e.g. "resume", "qa").
    Returns:
        Number of chunks stored."""
    if not chunks:
        return 0
    embedder   = get_embedder()
    collection = get_or_create_collection()
    existing_count = collection.count()
    ids = [f"{source_label}_{existing_count + i}" for i in range(len(chunks))]
    print(f"Embedding {len(chunks)} chunks from source='{source_label}'…")
    embeddings = embedder.encode(chunks, show_progress_bar=True).tolist()
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=[{"source": source_label}] * len(chunks)
    )
    print(f"✅ Stored {len(chunks)} chunks (collection total: {collection.count()})")
    return len(chunks)

def collection_count() -> int:
    """Return total number of chunks currently indexed."""
    try:
        return get_or_create_collection().count()
    except Exception:
        return 0

def reset_collection() -> None:
    """Delete the collection entirely so indexing starts fresh."""
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION)
        print("🗑️  Collection deleted.")
    except Exception:
        pass

if __name__ == "__main__":
    test_chunks = [
        "Explain the difference between a list and a tuple in Python.",
        "What is gradient descent and why is it used in machine learning?"
    ]
    n = embed_and_store(test_chunks, source_label="test")
    print(f"Stored {n} test chunks. Total in DB: {collection_count()}")
