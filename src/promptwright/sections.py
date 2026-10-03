"""Internal representation of prompt sections following PromtEngineering.md specification."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel


@dataclass
class Example:
    """Few-shot example representation."""
    input_text: str
    output_text: str
    description: Optional[str] = None


@dataclass
class ContextBlock:
    """Delimited context block (PromtEngineering.md §5, §10)."""
    name: str
    content: str
    tag: str = "context"
    treat_as_data: bool = True


@dataclass
class PromptSections:
    """Pure data model representing the engineered sections of a prompt (SRP)."""
    role: Optional[str] = None
    goal: Optional[str] = None
    context_blocks: List[ContextBlock] = field(default_factory=list)
    inputs: Dict[str, str] = field(default_factory=dict)
    tasks: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    output_schema: Optional[Type[BaseModel]] = None
    schema_mode: str = "full"  # "full" | "concise" | "tools_only"
    output_format_text: Optional[str] = None
    examples: List[Example] = field(default_factory=list)
    example_selector: Optional[Any] = None
    verifications: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def render_system_prompt(self, escape_braces_for_fstring: bool = True) -> str:
        """Backward-compatibility proxy delegating to MarkdownSectionRenderer."""
        from promptwright.renderers.markdown import MarkdownSectionRenderer
        return MarkdownSectionRenderer(escape_braces_for_fstring=escape_braces_for_fstring).render_system(self)
