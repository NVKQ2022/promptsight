"""Grounding middleware (PromtEngineering.md §14) for hallucination prevention and missing-data handling."""

from __future__ import annotations

from promptwright.middleware.base import SectionTransformer
from promptwright.sections import PromptSections


class StrictGroundingMiddleware(SectionTransformer):
    """Enforces grounding rules and handles ambiguous / missing values without guessing."""

    def __init__(
        self,
        allow_guessing: bool = False,
        missing_value_action: str = "mark as null/unknown",
    ):
        self.allow_guessing = allow_guessing
        self.missing_value_action = missing_value_action

    def transform(self, sections: PromptSections) -> PromptSections:
        new_constraints = list(sections.constraints)

        grounding_rule = "Use only information directly supported by the provided context."
        if not any("supported by the" in c.lower() for c in new_constraints):
            new_constraints.append(grounding_rule)

        if not self.allow_guessing:
            no_guess_rule = f"If required information is missing or ambiguous, {self.missing_value_action}. Do not invent or guess facts."
            if not any("do not invent" in c.lower() or "guess" in c.lower() for c in new_constraints):
                new_constraints.append(no_guess_rule)

        sections.constraints = new_constraints

        new_verifications = list(sections.verifications)
        check_item = "All claims and extracted fields are directly grounded in the source data."
        if not any("grounded" in v.lower() for v in new_verifications):
            new_verifications.append(check_item)

        sections.verifications = new_verifications
        return sections
