from loader    import load_uploaded_bytes
from chunker   import chunk_text
from embedder  import embed_and_store, collection_count, reset_collection
from retriever import retrieve
from generator import generate_rag_answer, generate_mock_question, evaluate_answer

def index_document(file_bytes: bytes, file_type: str, source_label: str) -> int:
    """
    Full indexing pipeline for an uploaded document.
    Stages: Load → Chunk → Embed → Store
    Args:
        file_bytes  : Raw bytes of the uploaded file.
        file_type   : "pdf" or "txt".
        source_label: Metadata tag stored with each chunk
                      (e.g. "resume", "qa_dataset").
    Returns:
        Number of chunks indexed."""
    text   = load_uploaded_bytes(file_bytes, file_type)
    chunks = chunk_text(text)
    n      = embed_and_store(chunks, source_label=source_label)
    return n
def ask(query: str) -> tuple[str, list[str]]:
    """
    Full RAG query pipeline.
    Stages: Embed query → Retrieve → Re-rank → Generate
    Args:
        query: Natural-language question from the user.
    Returns:
        (answer, context_chunks) — the LLM answer and the
        retrieved chunks that grounded it."""
    chunks = retrieve(query)
    answer = generate_rag_answer(query, chunks)
    return answer, chunks

def mock_question(topic: str) -> str:
    """
    Generate a single realistic interview question.
    Args:
        topic: Difficulty + subject, e.g. "Senior Machine Learning".
    Returns:
        Interview question string."""
    return generate_mock_question(topic)

def evaluate(question: str, user_answer: str) -> str:
    """
    Evaluate a candidate's answer and return structured feedback.
    Args:
        question   : The interview question.
        user_answer: Candidate's response.
    Returns:
        Structured evaluation with scores, strengths, and model answer."""
    return evaluate_answer(question, user_answer)

def get_collection_count() -> int:
    """Return total chunks in the vector store."""
    return collection_count()

def clear_knowledge_base() -> None:
    """Wipe the ChromaDB collection so indexing starts fresh."""
    reset_collection()
