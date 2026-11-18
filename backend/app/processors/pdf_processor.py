
from io import BytesIO

from pypdf import PdfReader


class PDFProcessingError(ValueError):
    pass


def process_pdf(content: bytes) -> dict:
    """
    Extract embedded text from PDF pages.
    OCR is handled separately by text_extractor.py.
    """
    try:
        reader = PdfReader(BytesIO(content), strict=True)

        if reader.is_encrypted:
            raise PDFProcessingError(
                "Encrypted PDFs are not supported."
            )

        page_count = len(reader.pages)

        if page_count > 200:
            raise PDFProcessingError(
                "PDF exceeds the 200-page processing limit."
            )

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()

            pages.append({
                "page": page_number,
                "text": text,
            })

        full_text = "\n\n".join(
            page["text"]
            for page in pages
            if page["text"]
        )

        return {
            "format": "pdf",
            "page_count": page_count,
            "pages": pages,
            "text": full_text,
            "character_count": len(full_text),
            "requires_ocr": any(
                not page["text"] for page in pages
            ),
        }

    except PDFProcessingError:
        raise

    except Exception as exc:
        raise PDFProcessingError(
            "Unable to process the PDF document."
        ) from exc
