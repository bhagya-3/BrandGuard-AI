import asyncio

from app.review_engine.suggestion.correction_generator import (
    CorrectionGenerator,
)


def test_configured_llm_generates_a_human_reviewed_suggestion(monkeypatch):
    generator = CorrectionGenerator()
    captured_messages = []

    async def generate_json(messages):
        captured_messages.extend(messages)
        return {
            "suggested_text": "A calmer, supported statement.",
            "rationale": "Avoids an unsupported guarantee.",
        }

    monkeypatch.setattr(generator.llm_client, "generate_json", generate_json)
    result = generator.generate(
        original_text="Guaranteed success.",
        finding={"title": "Unsupported claim"},
    )

    assert result["status"] == "suggested"
    assert result["suggested_text"] == "A calmer, supported statement."
    assert result["requires_human_review"] is True
    assert result["automatically_applied"] is False
    assert captured_messages[0]["role"] == "system"
    assert captured_messages[1]["role"] == "user"


def test_ai_request_rejects_running_event_loop():
    generator = CorrectionGenerator()

    async def request_from_loop():
        try:
            generator._request_ai("prompt")
        except RuntimeError as error:
            return str(error)
        raise AssertionError("Expected the active event loop to be rejected.")

    message = asyncio.run(request_from_loop())

    assert message == "AI suggestions must be requested outside an active event loop."
