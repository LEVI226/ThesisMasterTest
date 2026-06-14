"""
OCR Engine — Topic 1 (Fadel's domain): Deep Learning for OCR in Corporate Documents
Stub implementation using Tesseract for the demo.

Phase 2 migration: swap extract_from_file() to Azure Document Intelligence (Form Recognizer).
"""
import os
import logging
from pathlib import Path
from typing import Optional
import tempfile

from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

# Set Tesseract path from env (Windows)
tesseract_path = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Tesseract language config — FR + EN + DE
TESS_LANG = os.getenv("TESSERACT_LANGS", "fra+eng+deu")
TESS_CONFIG = "--oem 3 --psm 6"  # LSTM engine, uniform block of text


def _ocr_image(image: Image.Image) -> str:
    """Run Tesseract OCR on a PIL Image."""
    try:
        text = pytesseract.image_to_string(image, lang=TESS_LANG, config=TESS_CONFIG)
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        logger.error(
            "Tesseract not found. Install from: https://github.com/UB-Mannheim/tesseract/wiki"
        )
        return "[Tesseract not installed — OCR unavailable]"
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""


def extract_from_pdf(pdf_path: str) -> list[dict]:
    """
    Convert PDF pages to images and OCR each page.
    Uses pypdfium2 for robust cross-platform conversion.
    Returns list of {page, text} dicts.
    """
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(pdf_path)
        
        # Determine scale for rendering (200 DPI approx)
        # Standard PDF is 72 DPI, so scale 2.77 ≈ 200 DPI
        scale = 2.77
        
        pages = []
        for i, page in enumerate(pdf, start=1):
            bitmap = page.render(scale=scale)
            pil_image = bitmap.to_pil()
            
            text = _ocr_image(pil_image)
            pages.append({"page": i, "text": text})
            logger.info(f"OCR page {i}/{len(pdf)} — {len(text)} chars")
            
        pdf.close()
        return pages
        
    except ImportError:
        logger.error("pypdfium2 not installed.")
        return [{"page": 1, "text": "[pypdfium2 not installed — check dependencies]"}]
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        return [{"page": 1, "text": f"[PDF conversion error: {e}]"}]


def extract_from_image(image_path: str) -> list[dict]:
    """OCR a single image file (JPG, PNG, BMP, TIFF…)"""
    try:
        img = Image.open(image_path)
        # Enhance for better OCR accuracy
        img = img.convert("L")  # grayscale
        text = _ocr_image(img)
        return [{"page": 1, "text": text}]
    except Exception as e:
        logger.error(f"Image OCR failed: {e}")
        return [{"page": 1, "text": f"[OCR error: {e}]"}]


def extract_from_file(file_path: str) -> dict:
    """
    Main OCR entry point. Dispatches to PDF or image extractor.

    Phase 2 migration: replace this with Azure Document Intelligence call.
    See: https://learn.microsoft.com/azure/ai-services/document-intelligence/
    """
    ext = Path(file_path).suffix.lower()
    pdf_extensions = {".pdf"}
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

    if ext in pdf_extensions:
        pages = extract_from_pdf(file_path)
    elif ext in image_extensions:
        pages = extract_from_image(file_path)
    else:
        logger.warning(f"Unsupported file type: {ext}")
        pages = [{"page": 1, "text": f"[Unsupported file type: {ext}]"}]

    full_text = "\n\n".join(p["text"] for p in pages if p["text"])
    logger.info(
        f"OCR complete: {Path(file_path).name} | "
        f"{len(pages)} page(s) | {len(full_text)} total chars"
    )

    return {
        "pages": pages,
        "full_text": full_text,
        "detected_language": None,  # Can add langdetect here later
    }
