from app.processors.format_detector import detect_format
from app.processors.text_extractor import extract_text


def test_txt_format_detection():
    content = b"BrandGuard AI document"

    result = detect_format("sample.txt", content)

    assert result is not None


def test_txt_document_extraction():
    content = b"BrandGuard AI checks brand consistency."

    result = extract_text("sample.txt", content)

    assert isinstance(result, dict)
    assert "text" in result
    assert "BrandGuard AI" in result["text"]


def test_extracted_text_is_not_empty():
    content = b"This is a test document."

    result = extract_text("sample.txt", content)

    assert len(result["text"]) > 0