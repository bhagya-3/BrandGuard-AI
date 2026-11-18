from app.review_engine.deterministic.rule_engine import RuleEngine


def test_rule_engine_returns_results():
    engine = RuleEngine()

    result = engine.run(
        text="Our company provides reliable services.",
        rules=[],
        approved_claims=[],
    )

    assert isinstance(result, dict)
    assert "findings" in result


def test_rule_engine_finds_prohibited_term():
    engine = RuleEngine()

    rules = [
        {
            "rule_type": "prohibited_term",
            "match_type": "contains",
            "rule_config": {
                "term": "guaranteed",
            },
            "severity": "high",
            "is_active": True,
        }
    ]

    result = engine.run(
        text="We provide guaranteed results.",
        rules=rules,
        approved_claims=[],
    )

    assert len(result["findings"]) > 0