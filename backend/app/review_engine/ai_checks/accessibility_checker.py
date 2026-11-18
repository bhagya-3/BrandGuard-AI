
import re


class AccessibilityChecker:

    VAGUE_LINK_TEXT = {
        "click here",
        "read more",
        "learn more",
        "here",
        "know more",
    }

    def check(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> dict:

        findings = []
        metadata = metadata or {}

        if not text or not text.strip():
            return self._result(findings)

        # Detect image references without alternative text.
        image_pattern = r"!\[([^\]]*)\]\([^)]+\)"

        for match in re.finditer(image_pattern, text):
            alt_text = match.group(1).strip()

            if not alt_text:
                findings.append({
                    "category": "accessibility",
                    "severity": "medium",
                    "title": "Missing image alternative text",
                    "description": (
                        "An image does not contain alternative text."
                    ),
                    "evidence": match.group(),
                    "suggestion": (
                        "Provide meaningful alternative text "
                        "that describes the image."
                    ),
                })

        # Detect vague hyperlink labels.
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        for match in re.finditer(link_pattern, text):
            link_text = match.group(1).strip().lower()

            if link_text in self.VAGUE_LINK_TEXT:
                findings.append({
                    "category": "accessibility",
                    "severity": "low",
                    "title": "Unclear link text",
                    "description": (
                        "The link label does not clearly explain "
                        "its destination or purpose."
                    ),
                    "evidence": match.group(1),
                    "suggestion": (
                        "Use descriptive link text."
                    ),
                })

        # Check heading levels in Markdown content.
        heading_levels = []

        for match in re.finditer(r"^(#{1,6})\s+.+$", text, re.MULTILINE):
            heading_levels.append(len(match.group(1)))

        for previous, current in zip(
            heading_levels,
            heading_levels[1:],
        ):
            if current > previous + 1:
                findings.append({
                    "category": "accessibility",
                    "severity": "low",
                    "title": "Heading level skipped",
                    "description": (
                        "The heading structure skips one or more levels."
                    ),
                    "evidence": f"H{previous} to H{current}",
                    "suggestion": (
                        "Use a logical heading hierarchy."
                    ),
                })

        # Metadata can be supplied by document processors.
        images = metadata.get("images", [])

        for image in images:
            if isinstance(image, dict) and not image.get("alt_text"):
                findings.append({
                    "category": "accessibility",
                    "severity": "medium",
                    "title": "Image metadata missing alternative text",
                    "description": (
                        "An extracted image has no alternative text "
                        "in the supplied document metadata."
                    ),
                    "evidence": image.get("filename", "Unknown image"),
                    "suggestion": (
                        "Add an appropriate image description."
                    ),
                })

        return self._result(findings)

    @staticmethod
    def _result(findings: list[dict]) -> dict:
        return {
            "checker": "accessibility_checker",
            "passed": not any(
                item["severity"] in {"high", "critical"}
                for item in findings
            ),
            "finding_count": len(findings),
            "findings": findings,
        }
