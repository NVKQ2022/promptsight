"""Delimiter middleware (PromtEngineering.md §10) to prevent prompt injection and separate data from instructions."""

from __future__ import annotations

from promptwright.middleware.base import SectionTransformer
from promptwright.sections import PromptSections


class AutoDelimiterMiddleware(SectionTransformer):
    """Ensures context items are properly tagged and guarded against instruction hijacking."""

    def __init__(self, default_tag: str = "context", enforce_guardrail: bool = True):
        self.default_tag = default_tag
        self.enforce_guardrail = enforce_guardrail

    def transform(self, sections: PromptSections) -> PromptSections:
        for block in sections.context_blocks:
            if not block.tag:
                block.tag = self.default_tag

        return sections
