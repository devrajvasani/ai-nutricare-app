"""
PDF Parser Module.
Extracts text from PDF files using PyMuPDF (fitz) as primary engine,
with pdfplumber as fallback for table-heavy PDFs.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.utils.logger import logger
from app.utils.text_utils import clean_text, count_words


@dataclass
class PDFExtractionResult:
    """Structured result from PDF text extraction."""
    success: bool
    raw_text: str = ""
    page_texts: dict[str, str] = field(default_factory=dict)
    page_count: int = 0
    word_count: int = 0
    engine_used: str = ""
    error: Optional[str] = None


def extract_with_pymupdf(pdf_path: Path) -> PDFExtractionResult:
    """
    Extract text using PyMuPDF (fitz).
    Best for: standard PDFs with embedded text (fast, accurate).
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(pdf_path))
        page_texts: dict[str, str] = {}
        all_text_parts: list[str] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            cleaned = clean_text(text)
            page_key = f"page_{page_num + 1}"
            page_texts[page_key] = cleaned
            if cleaned:
                all_text_parts.append(cleaned)

        doc.close()

        raw_text = "\n\n".join(all_text_parts)

        return PDFExtractionResult(
            success=True,
            raw_text=raw_text,
            page_texts=page_texts,
            page_count=len(page_texts),
            word_count=count_words(raw_text),
            engine_used="pdfminer",  # PyMuPDF uses a similar label
        )

    except ImportError:
        logger.warning("PyMuPDF (fitz) not installed, falling back to pdfplumber.")
        return PDFExtractionResult(success=False, error="PyMuPDF not available.")
    except Exception as exc:
        logger.error(f"PyMuPDF extraction failed for {pdf_path.name}: {exc}")
        return PDFExtractionResult(success=False, error=str(exc))


def extract_with_pdfplumber(pdf_path: Path) -> PDFExtractionResult:
    """
    Extract text using pdfplumber.
    Best for: PDFs with tables (extracts table text in reading order).
    """
    try:
        import pdfplumber

        page_texts: dict[str, str] = {}
        all_text_parts: list[str] = []

        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                cleaned = clean_text(text)
                page_key = f"page_{page_num + 1}"
                page_texts[page_key] = cleaned
                if cleaned:
                    all_text_parts.append(cleaned)

        raw_text = "\n\n".join(all_text_parts)

        return PDFExtractionResult(
            success=True,
            raw_text=raw_text,
            page_texts=page_texts,
            page_count=len(page_texts),
            word_count=count_words(raw_text),
            engine_used="pdfplumber",
        )

    except ImportError:
        logger.warning("pdfplumber not installed.")
        return PDFExtractionResult(success=False, error="pdfplumber not available.")
    except Exception as exc:
        logger.error(f"pdfplumber extraction failed for {pdf_path.name}: {exc}")
        return PDFExtractionResult(success=False, error=str(exc))


def is_text_rich(text: str, min_words: int = 30) -> bool:
    """
    Determine whether the extracted text has meaningful content.
    Used to decide if OCR is needed for scanned PDFs.
    """
    return count_words(text) >= min_words


def parse_pdf(pdf_path: Path) -> PDFExtractionResult:
    """
    Main entry point for PDF parsing.
    Strategy:
        1. Try PyMuPDF (fastest, best for text PDFs)
        2. Try pdfplumber (better for tables)
        3. Return best result; if text is sparse, caller should run OCR
    """
    if not pdf_path.exists():
        return PDFExtractionResult(success=False, error=f"File not found: {pdf_path}")

    logger.info(f"Parsing PDF: {pdf_path.name}")

    # Try PyMuPDF first
    result = extract_with_pymupdf(pdf_path)

    if not result.success or not is_text_rich(result.raw_text):
        logger.info(f"PyMuPDF gave sparse results for {pdf_path.name}, trying pdfplumber.")
        fallback = extract_with_pdfplumber(pdf_path)
        if fallback.success and is_text_rich(fallback.raw_text):
            result = fallback

    if result.success:
        logger.info(
            f"PDF parsed: {result.page_count} pages, "
            f"{result.word_count} words via {result.engine_used}"
        )
    else:
        logger.warning(f"PDF parsing failed for {pdf_path.name}: {result.error}")

    return result