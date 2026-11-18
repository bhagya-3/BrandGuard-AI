from app.review_engine.suggestion.intent_preserver import IntentPreserver


def test_extract_numbers():
    checker = IntentPreserver()

    result = checker.extract_protected_elements(
        "Our service improves performance by 25%."
    )

    assert "25%" in result


def test_extract_email():
    checker = IntentPreserver()

    result = checker.extract_protected_elements(
        "Contact support@example.com for help."
    )

    assert "support@example.com" in result


def test_preserves_important_information():
    checker = IntentPreserver()

    original = "Our product costs ₹500 and saves 20% time."
    suggested = "Our product is affordable and saves time."

    result = checker.check(original, suggested)

    assert result["valid"] is False


def test_accepts_preserved_information():
    checker = IntentPreserver()

    original = "Our product costs ₹500."
    suggested = "The product is available for ₹500."

    result = checker.check(original, suggested)

    assert result["valid"] is True