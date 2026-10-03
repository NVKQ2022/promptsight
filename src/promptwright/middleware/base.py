"""Base definitions and protocols for promptwright middleware."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, List, Optional, Protocol, Union, runtime_checkable

from promptwright.sections import PromptSections


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
class Middleware(Protocol):
    """Protocol for promptwright middleware."""

    def transform(self, sections: PromptSections) -> PromptSections:
        """Transform or enrich prompt sections."""
        ...

    def validate(self, sections: PromptSections) -> List[ValidationIssue]:
        """Validate prompt sections against rules or anti-patterns."""
        ...


class BaseMiddleware:
    """Convenient base class with no-op defaults."""

    def transform(self, sections: PromptSections) -> PromptSections:
        return sections

    def validate(self, sections: PromptSections) -> List[ValidationIssue]:
        return []


MiddlewareType = Union[
    Middleware,
    Callable[[PromptSections], PromptSections],
    Callable[[PromptSections], List[ValidationIssue]],
]


def wrap_middleware(item: MiddlewareType) -> Middleware:
    """Normalize a callable or Middleware object into a compliant Middleware."""
    if isinstance(item, Middleware):
        return item

    if callable(item):
        class _CallableMiddleware(BaseMiddleware):
            def transform(self, sections: PromptSections) -> PromptSections:
                # If function returns PromptSections, it's a transform
                res = item(sections)
                if isinstance(res, PromptSections):
                    return res
                return sections

            def validate(self, sections: PromptSections) -> List[ValidationIssue]:
                res = item(sections)
                if isinstance(res, list) and all(isinstance(x, ValidationIssue) for x in res):
                    return res
                return []

        return _CallableMiddleware()

    raise TypeError(f"Expected Middleware or Callable, got {type(item)}")
