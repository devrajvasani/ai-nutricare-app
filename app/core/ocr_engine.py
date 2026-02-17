"""
OCR Engine Module.
Extracts text from scanned images and image-based PDFs.

Primary engine:  Tesseract (via pytesseract)
Fallback engine: EasyOCR (deep-learning based, better for noisy scans)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.config.settings import ocr_settings
from app.utils.logger import logger
from app.utils.text_utils import clean_text, count_words


@dataclass
class OCRResult:
    """Structured result from an OCR pass."""
    success: bool
    raw_text: str = ""
    page_texts: dict[str, str] = field(default_factory=dict)
    page_count: int = 0
    word_count: int = 0
    confidence: float = 0.0     # Average confidence (0–100)
    engine_used: str = ""
    error: Optional[str] = None


# ─── Tesseract ────────────────────────────────────────────────────────────────
def run_tesseract(image_path: Path) -> OCRResult:
    """
    Run Tesseract OCR on a single image file.
    Returns extracted text with average confidence score.
    """
    try:
        import pytesseract
        from PIL import Image

        pytesseract.pytesseract.tesseract_cmd = ocr_settings.TESSERACT_CMD

        img = Image.open(str(image_path))

        # Extract text
        text = pytesseract.image_to_string(img, lang=ocr_settings.LANGUAGE)

        # Extract confidence data
        data = pytesseract.image_to_data(
            img, lang=ocr_settings.LANGUAGE, output_type=pytesseract.Output.DICT
        )
        confidences = [
            c for c in data["conf"] if isinstance(c, (int, float)) and c >= 0
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        cleaned = clean_text(text)

        return OCRResult(
            success=True,
            raw_text=cleaned,
            page_texts={"page_1": cleaned},
            page_count=1,
            word_count=count_words(cleaned),
            confidence=round(avg_confidence, 2),
            engine_used="tesseract",
        )

    except ImportError:
        logger.warning("pytesseract not installed.")
        return OCRResult(success=False, error="pytesseract not available.")
    except Exception as exc:
        logger.error(f"Tesseract OCR failed for {image_path.name}: {exc}")
        return OCRResult(success=False, error=str(exc))


def run_tesseract_on_pdf(pdf_path: Path) -> OCRResult:
    """
    Convert each PDF page to an image and run Tesseract on each page.
    Used when the PDF is scanned (no embedded text).
    """
    try:
        import fitz  # PyMuPDF
        import pytesseract
        from PIL import Image
        import io

        pytesseract.pytesseract.tesseract_cmd = ocr_settings.TESSERACT_CMD
        doc = fitz.open(str(pdf_path))

        page_texts: dict[str, str] = {}
        all_confidences: list[float] = []
        all_text_parts: list[str] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render at 300 DPI for good OCR accuracy
            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")

            img = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(img, lang=ocr_settings.LANGUAGE)

            data = pytesseract.image_to_data(
                img, lang=ocr_settings.LANGUAGE, output_type=pytesseract.Output.DICT
            )
            confidences = [
                c for c in data["conf"] if isinstance(c, (int, float)) and c >= 0
            ]
            if confidences:
                all_confidences.extend(confidences)

            cleaned = clean_text(text)
            page_key = f"page_{page_num + 1}"
            page_texts[page_key] = cleaned
            if cleaned:
                all_text_parts.append(cleaned)

        doc.close()

        raw_text = "\n\n".join(all_text_parts)
        avg_confidence = (
            sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        )

        return OCRResult(
            success=True,
            raw_text=raw_text,
            page_texts=page_texts,
            page_count=len(page_texts),
            word_count=count_words(raw_text),
            confidence=round(avg_confidence, 2),
            engine_used="tesseract",
        )

    except Exception as exc:
        logger.error(f"Tesseract PDF OCR failed for {pdf_path.name}: {exc}")
        return OCRResult(success=False, error=str(exc))


# ─── EasyOCR ─────────────────────────────────────────────────────────────────
def run_easyocr(image_path: Path) -> OCRResult:
    """
    Run EasyOCR on a single image file.
    Better than Tesseract for low-quality, noisy, or rotated scans.
    """
    try:
        import easyocr

        reader = easyocr.Reader([ocr_settings.LANGUAGE], gpu=False)
        results = reader.readtext(str(image_path))

        lines: list[str] = []
        confidences: list[float] = []

        for _bbox, text, confidence in results:
            lines.append(text)
            confidences.append(confidence * 100)  # EasyOCR returns 0-1

        raw_text = clean_text(" ".join(lines))
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return OCRResult(
            success=True,
            raw_text=raw_text,
            page_texts={"page_1": raw_text},
            page_count=1,
            word_count=count_words(raw_text),
            confidence=round(avg_confidence, 2),
            engine_used="easyocr",
        )

    except ImportError:
        logger.warning("easyocr not installed.")
        return OCRResult(success=False, error="easyocr not available.")
    except Exception as exc:
        logger.error(f"EasyOCR failed for {image_path.name}: {exc}")
        return OCRResult(success=False, error=str(exc))


# ─── Main Entry Point ─────────────────────────────────────────────────────────
def run_ocr(file_path: Path, file_type: str) -> OCRResult:
    """
    Route the file to the correct OCR strategy based on file type and config.

    Args:
        file_path: Path to the file (image or PDF).
        file_type: 'image' | 'pdf'
    """
    logger.info(f"Starting OCR on {file_path.name} (type={file_type})")

    engine = ocr_settings.ENGINE.lower()

    if file_type == "image":
        if engine == "easyocr":
            result = run_easyocr(file_path)
            if not result.success:
                logger.warning("EasyOCR failed, falling back to Tesseract.")
                result = run_tesseract(file_path)
        else:
            result = run_tesseract(file_path)
            if not result.success:
                logger.warning("Tesseract failed, falling back to EasyOCR.")
                result = run_easyocr(file_path)

    elif file_type == "pdf":
        # For PDFs, run Tesseract page-by-page
        result = run_tesseract_on_pdf(file_path)
        if not result.success:
            return OCRResult(success=False, error="All OCR engines failed for PDF.")

    else:
        return OCRResult(success=False, error=f"Unsupported file_type: {file_type}")

    if result.success:
        logger.info(
            f"OCR complete: {result.word_count} words, "
            f"confidence={result.confidence:.1f}%, engine={result.engine_used}"
        )
    return result