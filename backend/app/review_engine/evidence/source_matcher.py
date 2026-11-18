
import re
from typing import Any


class SourceMatcher:

    def __init__(self, minimum_score: float = 0.35):
        self.minimum_score = minimum_score

    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s%]", " ", text)
        return " ".join(text.split())

    @staticmethod
    def tokenize(text: str) -> set[str]:
        return set(SourceMatcher.normalize(text).split())

    def calculate_similarity(
        self,
        query: str,
        source_text: str,
    ) -> float:

        query_tokens = self.tokenize(query)
        source_tokens = self.tokenize(source_text)

        if not query_tokens or not source_tokens:
            return 0.0

        intersection = query_tokens.intersection(source_tokens)

        # Query coverage: how much of the query appears in the source.
        return len(intersection) / len(query_tokens)

    def split_into_chunks(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 80,
    ) -> list[str]:

        if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
            raise ValueError("Invalid chunk size or overlap.")

        words = text.split()
        chunks = []

        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])

            if chunk.strip():
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    def match_sources(
        self,
        query: str,
        sources: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[dict]:

        if not query or not query.strip():
            return []

        if top_k <= 0:
            return []

        matches = []

        for source in sources:

            if source.get("status") != "approved":
                continue

            source_text = source.get("content", "")

            if not isinstance(source_text, str) or not source_text.strip():
                continue

            chunks = self.split_into_chunks(source_text)

            for index, chunk in enumerate(chunks):

                score = self.calculate_similarity(query, chunk)

                if score < self.minimum_score:
                    continue

                matches.append({
                    "source_id": source.get("source_id"),
                    "source_version_id": source.get("source_version_id"),
                    "source_title": source.get("title"),
                    "chunk_index": index,
                    "content": chunk,
                    "relevance_score": round(score, 4),
                    "source_status": source.get("status"),
                })

        matches.sort(
            key=lambda item: item["relevance_score"],
            reverse=True,
        )

        return matches[:top_k]
