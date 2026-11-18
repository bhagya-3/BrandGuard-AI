
from io import BytesIO

from docx import Document


class DOCXProcessingError(ValueError):
    pass


def process_docx(content: bytes) -> dict:
    try:
        document = Document(BytesIO(content))

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        tables = []

        for table_index, table in enumerate(document.tables, start=1):
            rows = []

            for row in table.rows:
                rows.append([
                    cell.text.strip()
                    for cell in row.cells
                ])

            tables.append({
                "table": table_index,
                "rows": rows,
            })

        table_text = []

        for table in tables:
            for row in table["rows"]:
                table_text.append(" | ".join(row))

        full_text = "\n".join(paragraphs + table_text)

        return {
            "format": "docx",
            "paragraphs": paragraphs,
            "tables": tables,
            "text": full_text,
            "character_count": len(full_text),
        }

    except Exception as exc:
        raise DOCXProcessingError(
            "Unable to process the Word document."
        ) from exc
