"""Extract plain text from PDF, DOCX, or TXT resume files."""
import io
from typing import Tuple
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document


def extract_text(file_storage) -> Tuple[str, str]:
    """Return (text, file_type). Raises ValueError on unsupported / unreadable files."""
    filename = (file_storage.filename or "").lower()
    raw = file_storage.read()
    file_storage.seek(0)

    if not raw:
        raise ValueError("Uploaded file is empty.")

    if filename.endswith(".pdf"):
        text = pdf_extract_text(io.BytesIO(raw)) or ""
        ftype = "pdf"
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(raw))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        ftype = "docx"
    elif filename.endswith(".txt"):
        text = raw.decode("utf-8", errors="ignore")
        ftype = "txt"
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

    text = text.strip()
    if len(text) < 30:
        raise ValueError(
            "Could not read enough text from the file. "
            "If it's a scanned PDF (image), paste the text manually instead."
        )
    return text, ftype
