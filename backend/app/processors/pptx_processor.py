
from io import BytesIO

from pptx import Presentation


class PPTXProcessingError(ValueError):
    pass


def process_pptx(content: bytes) -> dict:
    try:
        presentation = Presentation(BytesIO(content))

        if len(presentation.slides) > 300:
            raise PPTXProcessingError(
                "Presentation exceeds the 300-slide limit."
            )

        slides = []

        for slide_number, slide in enumerate(
            presentation.slides, start=1
        ):
            slide_text = []

            for shape in slide.shapes:
                if shape.has_text_frame:
                    text = shape.text.strip()

                    if text:
                        slide_text.append(text)

                if shape.has_table:
                    for row in shape.table.rows:
                        values = [
                            cell.text.strip()
                            for cell in row.cells
                        ]

                        slide_text.append(" | ".join(values))

            slides.append({
                "slide": slide_number,
                "text": "\n".join(slide_text),
            })

        full_text = "\n\n".join(
            slide["text"] for slide in slides
        )

        return {
            "format": "pptx",
            "slide_count": len(slides),
            "slides": slides,
            "text": full_text,
            "character_count": len(full_text),
        }

    except PPTXProcessingError:
        raise

    except Exception as exc:
        raise PPTXProcessingError(
            "Unable to process the PowerPoint presentation."
        ) from exc
