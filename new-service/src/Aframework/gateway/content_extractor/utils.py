"""Shared file utilities for content extractors."""

import logging
import os

import fitz

logger = logging.getLogger(__name__)


def read_binary_file(filepath: str) -> bytes:
    """Read a file in binary mode and return its content as bytes."""
    try:
        with open(filepath, "rb") as file:
            return file.read()
    except FileNotFoundError:
        raise
    except OSError as error:
        raise IOError(f"Failed to read file: {error}") from error


def extract_pdf_text(file_content: bytes) -> str:
    """Extract plain text from PDF bytes, decrypting with PDF_PASSWORD if needed."""
    password = os.getenv("PDF_PASSWORD")
    pdf_document = fitz.open(stream=file_content, filetype="pdf")

    if pdf_document.is_encrypted:
        if password:
            if not pdf_document.authenticate(password):
                raise ValueError("Incorrect password for PDF")
        else:
            raise ValueError("PDF is encrypted but no password provided")

    logger.info(f"PDF has {pdf_document.page_count} pages")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        page_text = page.get_text()
        if page_text:
            text += f"\n\n--- PAGE {page_num + 1} ---\n\n{page_text}\n"

    pdf_document.close()
    return text