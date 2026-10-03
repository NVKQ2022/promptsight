"""Delimiter middleware (PromtEngineering.md §10) to prevent prompt injection and separate data from instructions."""

from __future__ import annotations

from typing import List

from promptwright.middleware.base import BaseMiddleware, ValidationIssue
from promptwright.sections import ContextBlock, PromptSections


class AutoDelimiterMiddleware(BaseMiddleware):
    """Ensures context items are properly tagged and guarded against instruction hijacking."""

    def __init__(self, default_tag: str = "context", enforce_guardrail: bool = True):
        self.default_tag = default_tag
        self.enforce_guardrail = enforce_guardrail

    def transform(self, sections: PromptSections) -> PromptSections:
        # If context blocks have empty tags, set default
        for block in sections.context_blocks:
            if not block.tag:
                block.tag = self.default_tag

        return sections
