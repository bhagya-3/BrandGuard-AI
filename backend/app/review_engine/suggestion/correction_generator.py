
import asyncio
import json
import re
from typing import Any

from app.ai_engine.llm_client import LLMClient
from app.ai_engine.prompt_manager import PromptManager

from app.review_engine.suggestion.intent_preserver import (
    IntentPreserver,
)


class CorrectionGenerator:

    def __init__(self):
        self.llm_client = LLMClient()
        self.prompt_manager = PromptManager()
        self.intent_preserver = IntentPreserver()

    def generate(
        self,
        original_text: str,
        finding: dict[str, Any],
        brand_guidelines: dict[str, Any] | None = None,
        evidence: list[dict[str, Any]] | None = None,
        protected_terms: list[str] | None = None,
    ) -> dict[str, Any]:

        if not original_text or not original_text.strip():
            raise ValueError("Original text is required.")

        guidelines = brand_guidelines or {}
        evidence = evidence or []

        prompt = self._build_prompt(
            original_text=original_text,
            finding=finding,
            brand_guidelines=guidelines,
            evidence=evidence,
        )

        try:
            response = self._request_ai(prompt)
            suggestion = self._parse_response(response)

            suggested_text = suggestion["suggested_text"]

            preservation = self.intent_preserver.check(
                original_text=original_text,
                suggested_text=suggested_text,
                protected_terms=protected_terms,
            )

            if not preservation["preserved"]:
                return {
                    "status": "needs_review",
                    "suggested_text": suggested_text,
                    "rationale": suggestion["rationale"],
                    "intent_preservation": preservation,
                    "message": (
                        "The proposed correction changed protected "
                        "information. Human verification is required."
                    ),
                    "requires_human_review": True,
                }

            return {
                "status": "suggested",
                "suggested_text": suggested_text,
                "rationale": suggestion["rationale"],
                "intent_preservation": preservation,
                "requires_human_review": True,
                "automatically_applied": False,
            }

        except Exception as exc:
            return {
                "status": "unavailable",
                "suggested_text": None,
                "rationale": (
                    "An AI correction could not be generated. "
                    "A reviewer can make the correction manually."
                ),
                "error": str(exc),
                "requires_human_review": True,
                "automatically_applied": False,
            }

    def _build_prompt(
        self,
        original_text: str,
        finding: dict,
        brand_guidelines: dict,
        evidence: list[dict],
    ) -> str:

        safe_finding = {
            "title": finding.get("title"),
            "description": finding.get("description"),
            "category": finding.get("category"),
            "severity": finding.get("severity"),
            "evidence": finding.get("evidence"),
        }

        safe_evidence = [
            {
                "source_title": item.get("source_title"),
                "quoted_text": item.get("quoted_text"),
                "source_version_id": item.get("source_version_id"),
            }
            for item in evidence
        ]

        return f"""
You are a careful brand-compliance writing assistant.

Your task is to suggest a correction for the supplied text.

RULES:
1. Preserve the original meaning and intent.
2. Do not invent facts, figures, statistics or promises.
3. Follow the supplied brand guidelines.
4. Use approved evidence only when it supports the correction.
5. Do not remove important product details.
6. Do not claim that a correction is legally or factually verified.
7. Return JSON only.
8. Never approve or publish the document.

ORIGINAL TEXT:
{original_text}

REVIEW FINDING:
{json.dumps(safe_finding, ensure_ascii=False)}

BRAND GUIDELINES:
{json.dumps(brand_guidelines, ensure_ascii=False)}

APPROVED SOURCE EVIDENCE:
{json.dumps(safe_evidence, ensure_ascii=False)}

Return this JSON structure:
{{
    "suggested_text": "Corrected text",
    "rationale": "Explanation of the correction"
}}
"""

    def _request_ai(self, prompt: str) -> dict:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(
                self.llm_client.generate_json(
                    [
                        {
                            "role": "system",
                            "content": (
                                "Return only a JSON object with "
                                "suggested_text and rationale."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ]
                )
            )
        raise RuntimeError(
            "AI suggestions must be requested outside an active event loop."
        )

    @staticmethod
    def _parse_response(response: Any) -> dict:

        if isinstance(response, dict):
            data = response
        else:
            content = str(response).strip()

            # Remove optional Markdown JSON fences.
            content = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                content,
                flags=re.IGNORECASE,
            )

            data = json.loads(content)

        suggested_text = data.get("suggested_text")
        rationale = data.get("rationale")

        if not isinstance(suggested_text, str) or not suggested_text.strip():
            raise ValueError("AI response has no valid suggested_text.")

        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("AI response has no valid rationale.")

        return {
            "suggested_text": suggested_text.strip(),
            "rationale": rationale.strip(),
        }
