
from typing import Any


class VisualChecker:

    def check(
        self,
        visual_data: dict[str, Any] | None = None,
        brand_guidelines: dict[str, Any] | None = None,
    ) -> dict:

        findings = []

        visual_data = visual_data or {}
        brand_guidelines = brand_guidelines or {}

        if not visual_data:
            return {
                "checker": "visual_checker",
                "passed": True,
                "finding_count": 0,
                "findings": [],
                "status": "not_evaluated",
                "message": (
                    "No visual inspection data was supplied. "
                    "Visual compliance has not been verified."
                ),
            }

        approved_colors = {
            color.lower()
            for color in brand_guidelines.get("approved_colors", [])
            if isinstance(color, str)
        }

        detected_colors = {
            color.lower()
            for color in visual_data.get("detected_colors", [])
            if isinstance(color, str)
        }

        if approved_colors and detected_colors:
            unapproved = detected_colors - approved_colors

            for color in sorted(unapproved):
                findings.append({
                    "category": "visual",
                    "severity": "medium",
                    "title": "Unapproved brand color detected",
                    "description": (
                        "A detected color is not listed in the "
                        "approved brand color palette."
                    ),
                    "evidence": color,
                    "suggestion": (
                        "Verify whether this color is permitted "
                        "for this document or campaign."
                    ),
                })

        required_logo = brand_guidelines.get("logo_required", False)
        logo_detected = visual_data.get("logo_detected")

        if required_logo and logo_detected is False:
            findings.append({
                "category": "visual",
                "severity": "high",
                "title": "Required brand logo not detected",
                "description": (
                    "The visual inspection data indicates that "
                    "the required logo is missing."
                ),
                "evidence": "logo_detected=False",
                "suggestion": (
                    "Verify the document and add the approved logo "
                    "if required."
                ),
            })

        minimum_width = brand_guidelines.get("minimum_logo_width")
        logo_width = visual_data.get("logo_width")

        if (
            minimum_width is not None
            and logo_width is not None
            and logo_width < minimum_width
        ):
            findings.append({
                "category": "visual",
                "severity": "medium",
                "title": "Logo may be too small",
                "description": (
                    "The detected logo width is below the "
                    "configured minimum."
                ),
                "evidence": f"Detected width: {logo_width}",
                "suggestion": (
                    "Check the official logo sizing guidelines."
                ),
            })

        return {
            "checker": "visual_checker",
            "passed": not any(
                item["severity"] in {"high", "critical"}
                for item in findings
            ),
            "finding_count": len(findings),
            "findings": findings,
            "status": "evaluated",
        }
