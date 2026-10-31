"""Read text out of PDF, DOCX and TXT files."""
import io
import re

from docx import Document
from pypdf import PdfReader


def clean_text(text):
    """Normalise whitespace and drop empty lines."""
    text = text.replace("\r", "\n").replace("\x00", " ")
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def extract_text(filename, data):
    """Turn an uploaded file into clean text. Raises ValueError for unsupported types."""
    name = (filename or "").lower()

    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\n".join(pages)

    elif name.endswith(".docx"):
        document = Document(io.BytesIO(data))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    elif name.endswith(".txt"):
        text = data.decode("utf-8", errors="ignore")

    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX or TXT file.")

    return clean_text(text)
