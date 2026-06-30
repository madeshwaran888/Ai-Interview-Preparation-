from sentence_transformers import CrossEncoder
from config import RERANK_MODEL, TOP_K, RERANK_TOP_N
from embedder import get_embedder, get_or_create_collection
_reranker: CrossEncoder | None = None

def get_reranker() -> CrossEncoder:
    """Lazy-load the cross-encoder re-ranker."""
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANK_MODEL)
    return _reranker

def retrieve(query: str, top_k: int = TOP_K, rerank_top_n: int = RERANK_TOP_N) -> list[str]:
    """
    Full retrieval pipeline: embed → vector search → re-rank.
    Args:
        query        : The user's natural-language question.
        top_k        : Candidate pool size from ChromaDB.
        rerank_top_n : How many chunks to keep after re-ranking.
    Returns:
        List of the most relevant text chunks (length ≤ rerank_top_n).
        Returns an empty list if the collection is empty."""
    collection = get_or_create_collection()
    total = collection.count()
    if total == 0:
        return []
    embedder  = get_embedder()
    query_vec = embedder.encode(query).tolist()
    n_results  = min(top_k, total)  
    results    = collection.query(
        query_embeddings=[query_vec],
        n_results=n_results
    )
    candidates: list[str] = results["documents"][0]
    if not candidates:
        return []
    reranker = get_reranker()
    pairs    = [(query, chunk) for chunk in candidates]
    scores   = reranker.predict(pairs)          
    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in ranked[:rerank_top_n]]
if __name__ == "__main__":
    query  = "What is the difference between bagging and boosting?"
    chunks = retrieve(query)
    if not chunks:
        print("No chunks in the database yet. Run embedder.py first.")
    else:
        print(f"Top {len(chunks)} chunks for: '{query}'\n")
        for i, c in enumerate(chunks, 1):
            print(f"--- Chunk {i} ---\n{c[:300]}\n")
