
from io import BytesIO

from PIL import Image, UnidentifiedImageError


class ImageProcessingError(ValueError):
    pass


MAX_IMAGE_PIXELS = 25_000_000


def process_image(content: bytes) -> dict:
    try:
        with Image.open(BytesIO(content)) as image:
            image_format = image.format
            width, height = image.size

            if width * height > MAX_IMAGE_PIXELS:
                raise ImageProcessingError(
                    "Image dimensions exceed the processing limit."
                )

            image.verify()

        return {
            "format": "image",
            "image_format": image_format,
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 3),
            "requires_ocr": True,
        }

    except ImageProcessingError:
        raise

    except (UnidentifiedImageError, OSError) as exc:
        raise ImageProcessingError(
            "Invalid or unsupported image."
        ) from exc
