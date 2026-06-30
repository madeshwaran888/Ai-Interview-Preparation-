import fitz  # PyMuPDF
def load_pdf(path: str) -> str:
    """
    Extract all text from a PDF file page by page.
    Args:
        path: Absolute or relative path to the .pdf file.
    Returns:
        Full document text as a single string.
    """
    doc = fitz.open(path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)

def load_text_file(path: str) -> str:
    """
    Read a UTF-8 plain-text file (e.g. interview Q&A dataset).
    Args:
        path: Path to the .txt file.
    Returns:
        File contents as a string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_uploaded_bytes(file_bytes: bytes, file_type: str) -> str:
    """
    Load content from in-memory bytes (e.g. Streamlit UploadedFile).
    Args:
        file_bytes : Raw bytes of the uploaded file.
        file_type  : "pdf" or "txt".
    Returns:
        Extracted text string."""
    if file_type == "pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text
    if file_type == "txt":
        return file_bytes.decode("utf-8")
    raise ValueError(f"Unsupported file type: {file_type}")
