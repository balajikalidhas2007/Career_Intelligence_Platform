"""Resume text extraction from PDF and DOCX files."""

import io

import pdfplumber
from docx import Document


SUPPORTED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from a PDF file."""
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from a DOCX file."""
    doc = Document(io.BytesIO(content))
    return "\n\n".join(para.text for para in doc.paragraphs if para.text.strip())


def extract_text(content: bytes, content_type: str) -> str:
    """Extract text from a resume file based on content type.

    Raises ValueError if the content type is unsupported or extraction fails.
    """
    fmt = SUPPORTED_CONTENT_TYPES.get(content_type)
    if not fmt:
        raise ValueError(f"Unsupported file type: {content_type}")

    if fmt == "pdf":
        text = extract_text_from_pdf(content)
    elif fmt == "docx":
        text = extract_text_from_docx(content)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    if not text or not text.strip():
        raise ValueError("Could not extract any text from the file")

    return text.strip()
