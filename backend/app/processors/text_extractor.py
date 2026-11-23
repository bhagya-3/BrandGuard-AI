
from io import BytesIO
import math


from app.processors.pdf_processor import (
    process_pdf,
    PDFProcessingError,
)
from app.processors.docx_processor import process_docx
from app.processors.pptx_processor import process_pptx
from app.processors.image_processor import process_image
from app.processors.ocr_processor import (
    extract_text_from_image,
    OCRProcessingError,
)
from app.processors.format_detector import detect_format


MAX_PDF_PAGES = 200
MAX_OCR_PIXELS = 25_000_000


class TextExtractionError(ValueError):
    pass


def extract_text_from_pdf_with_ocr(
    content: bytes,
    result: dict,
) -> dict:
    try:
        import pymupdf
    except Exception as exc:
        raise TextExtractionError(
            "PDF OCR requires PyMuPDF, but its native library could not be loaded."
        ) from exc

    ocr_pages = []

    try:
        with pymupdf.open(
            stream=content,
            filetype="pdf",
        ) as pdf_document:

            if pdf_document.page_count > MAX_PDF_PAGES:
                raise TextExtractionError(
                    "PDF exceeds the 200-page processing limit."
                )

            for index, page_data in enumerate(result["pages"]):

                # Skip pages that already contain extractable text.
                if page_data["text"].strip():
                    continue

                page = pdf_document.load_page(index)

                # Estimate rendered dimensions before allocating memory.
                width = math.ceil(page.rect.width * 2)
                height = math.ceil(page.rect.height * 2)

                if width <= 0 or height <= 0:
                    raise TextExtractionError(
                        f"Invalid dimensions on PDF page {index + 1}."
                    )

                if width * height > MAX_OCR_PIXELS:
                    raise TextExtractionError(
                        f"PDF page {index + 1} exceeds the OCR image limit."
                    )

                pixmap = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False,
                )

                if pixmap.width * pixmap.height > MAX_OCR_PIXELS:
                    raise TextExtractionError(
                        f"PDF page {index + 1} exceeds the OCR image limit."
                    )

                image_bytes = pixmap.tobytes("png")

                ocr_result = extract_text_from_image(image_bytes)

                page_data["text"] = ocr_result["text"].strip()

                ocr_pages.append({
                    "page": index + 1,
                    "character_count": ocr_result["character_count"],
                    "engine": ocr_result["engine"],
                    "language": ocr_result["language"],
                })

        full_text = "\n\n".join(
            page["text"]
            for page in result["pages"]
            if page["text"].strip()
        )

        result.update({
            "text": full_text,
            "character_count": len(full_text),
            "requires_ocr": False,
            "ocr": {
                "used": bool(ocr_pages),
                "engine": "tesseract",
                "pages": ocr_pages,
            },
        })

        if not full_text.strip():
            raise TextExtractionError(
                "No readable text could be extracted from the PDF, "
                "even after OCR."
            )

        return result

    except (TextExtractionError, OCRProcessingError):
        raise

    except Exception as exc:
        raise TextExtractionError(
            "Unable to convert PDF pages for OCR."
        ) from exc


def extract_text(
    filename: str,
    content: bytes,
    use_ocr: bool = True,
) -> dict:

    file_format = detect_format(filename, content)

    try:
        if file_format == "pdf":
            result = process_pdf(content)

            if result["requires_ocr"] and use_ocr:
                result = extract_text_from_pdf_with_ocr(
                    content,
                    result,
                )

        elif file_format == "docx":
            result = process_docx(content)

        elif file_format == "pptx":
            result = process_pptx(content)

        elif file_format in ("png", "jpeg", "webp"):
            image_result = process_image(content)

            result = {
                **image_result,
                "text": "",
                "character_count": 0,
            }

            if use_ocr:
                ocr_result = extract_text_from_image(content)

                result.update({
                    "text": ocr_result["text"],
                    "character_count": ocr_result["character_count"],
                    "ocr": ocr_result,
                })

        elif file_format == "txt":
            text = content.decode("utf-8")

            result = {
                "format": "txt",
                "text": text,
                "character_count": len(text),
            }

        else:
            raise TextExtractionError(
                "Unsupported file format."
            )

        return result

    except (
        TextExtractionError,
        PDFProcessingError,
    ):
        raise

    except Exception as exc:
        raise TextExtractionError(
            "Failed to extract text from the uploaded file."
        ) from exc
