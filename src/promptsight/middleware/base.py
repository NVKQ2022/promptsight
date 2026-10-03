"""Base definitions and segregated protocols for promptsight middleware (ISP & LSP)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    List,
    Optional,
    Protocol,
    Union,
    runtime_checkable,
)

from promptsight.sections import PromptSections


class IssueSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    code: str
    message: str
    section: str
    severity: IssueSeverity = IssueSeverity.WARNING
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        s = f"[{self.severity.value.upper()}] ({self.section}) {self.message}"
        if self.suggestion:
            s += f" -> Suggestion: {self.suggestion}"
        return s


@runtime_checkable
class SectionTransformer(Protocol):
    """ISP: Interface dedicated strictly to section transformation."""

    def transform(self, sections: PromptSections) -> PromptSections: ...


@runtime_checkable
class PromptValidator(Protocol):
    """ISP: Interface dedicated strictly to prompt validation."""

    def validate(self, sections: PromptSections) -> List[ValidationIssue]: ...


@runtime_checkable
class Middleware(SectionTransformer, PromptValidator, Protocol):
    """Composite interface for components that both transform and validate."""

    ...


class BaseMiddleware:
    """Convenient base class providing default no-op implementations for both."""

    def transform(self, sections: PromptSections) -> PromptSections:
        return sections

    def validate(self, sections: PromptSections) -> List[ValidationIssue]:
        return []


PipelineComponent = Union[
    SectionTransformer,
    PromptValidator,
    Callable[[PromptSections], PromptSections],
    Callable[[PromptSections], List[ValidationIssue]],
]


def is_transformer(component: Any) -> bool:
    """Check if component provides a transform operation."""
    return hasattr(component, "transform") and callable(getattr(component, "transform"))


def is_validator(component: Any) -> bool:
    """Check if component provides a validate operation."""
    return hasattr(component, "validate") and callable(getattr(component, "validate"))
