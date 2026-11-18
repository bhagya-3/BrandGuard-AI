
from io import BytesIO

from PIL import Image, UnidentifiedImageError
import pytesseract

from app.core.logging import get_logger

logger = get_logger(__name__)


class OCRProcessingError(ValueError):
    pass


def extract_text_from_image(
    content: bytes,
    language: str = "eng",
) -> dict:
    try:
        with Image.open(BytesIO(content)) as image:
            image.load()

            if image.width * image.height > 25_000_000:
                raise OCRProcessingError(
                    "Image exceeds the OCR dimension limit."
                )

            image = image.convert("RGB")

            text = pytesseract.image_to_string(
                image,
                lang=language,
                timeout=30,
            )

        return {
            "text": text.strip(),
            "character_count": len(text.strip()),
            "language": language,
            "engine": "tesseract",
        }

    except OCRProcessingError:
        raise

    except pytesseract.TesseractNotFoundError as exc:
        logger.exception("Tesseract OCR is not installed.")
        raise OCRProcessingError(
            "Tesseract OCR is unavailable. Install it and configure PATH."
        ) from exc

    except pytesseract.TesseractError as exc:
        logger.exception("OCR engine failed.")
        raise OCRProcessingError(
            "OCR could not process this image."
        ) from exc

    except (UnidentifiedImageError, OSError) as exc:
        raise OCRProcessingError(
            "Unable to open the uploaded image."
        ) from exc
