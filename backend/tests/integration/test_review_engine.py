from app.review_engine.deterministic.rule_engine import RuleEngine
from app.review_engine.ai_checks.readability_checker import ReadabilityChecker
from app.review_engine.ai_checks.tone_checker import ToneChecker


def test_deterministic_review_integration():
    engine = RuleEngine()

    result = engine.run(
        text="We provide guaranteed results to every customer.",
        rules=[
            {
                "rule_type": "prohibited_term",
                "match_type": "contains",
                "rule_config": {"term": "guaranteed"},
                "severity": "high",
                "is_active": True,
            }
        ],
        approved_claims=[],
    )

    assert isinstance(result["findings"], list)
    assert len(result["findings"]) > 0


def test_readability_and_tone_checks():
    text = (
        "Hey! This is an extremely long sentence that contains "
        "many words and should be checked by the readability checker."
    )

    readability = ReadabilityChecker().check(text)
    tone = ToneChecker().check(text)

    assert isinstance(readability, dict)
    assert isinstance(tone, dict)