"""Abstract base and protocol for prompt renderers (SRP & DIP)."""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from promptsight.sections import PromptSections


@runtime_checkable
class PromptRenderer(Protocol):
    """Protocol defining the contract for rendering PromptSections into template strings."""

    def render_system(self, sections: PromptSections) -> str:
        """Render the system prompt message string."""
        ...

    def render_user(
        self,
        sections: PromptSections,
        custom_template: Optional[str] = None,
    ) -> str:
        """Render the human/user prompt message string."""
        ...
