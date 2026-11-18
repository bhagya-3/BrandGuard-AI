from app.review_engine.evidence.source_matcher import SourceMatcher
from app.review_engine.evidence.citation_builder import CitationBuilder


def test_only_approved_sources_are_matched():
    matcher = SourceMatcher(minimum_score=0.1)

    sources = [
        {
            "source_id": "source-1",
            "source_version_id": "version-1",
            "title": "Approved Brand Guide",
            "content": "Our brand uses a professional and friendly tone.",
            "status": "approved",
        },
        {
            "source_id": "source-2",
            "source_version_id": "version-2",
            "title": "Unapproved Guide",
            "content": "Our brand uses a casual tone.",
            "status": "pending",
        },
    ]

    results = matcher.match_sources(
        "professional brand tone",
        sources,
    )

    assert all(item["source_id"] == "source-1" for item in results)


def test_citation_builder():
    builder = CitationBuilder()

    source_match = {
        "source_id": "source-1",
        "source_version_id": "version-1",
        "title": "Approved Brand Guide",
        "content": "Use a professional tone.",
        "relevance_score": 0.9,
        "chunk_index": 0,
        "status": "approved",
    }

    result = builder.build_citation(source_match)

    assert result["source_id"] == "source-1"
    assert result["source_version_id"] == "version-1"