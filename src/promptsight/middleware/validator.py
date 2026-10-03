"""Composite AntiPatternValidator executing modular validation rules (SRP, OCP, DIP)."""

from __future__ import annotations

from typing import List, Optional, Sequence

from promptsight.middleware.base import PromptValidator, ValidationIssue
from promptsight.middleware.rules import (
    ConstraintsStyleRule,
    OutputFormatRule,
    RoleAndGoalRule,
    TaskClarityRule,
    ValidationRule,
    VerificationChecklistRule,
)
from promptsight.sections import PromptSections

DEFAULT_RULES: Sequence[ValidationRule] = (
    RoleAndGoalRule(),
    TaskClarityRule(),
    OutputFormatRule(),
    ConstraintsStyleRule(),
    VerificationChecklistRule(),
)


class AntiPatternValidator(PromptValidator):
    """Quality Gate validator composed of independent, extensible validation rules."""

    def __init__(
        self,
        rules: Optional[Sequence[ValidationRule]] = None,
        strict: bool = False,
    ):
        self.rules: Sequence[ValidationRule] = rules if rules is not None else DEFAULT_RULES
        self.strict = strict

    def validate(self, sections: PromptSections) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        for rule in self.rules:
            issues.extend(rule.evaluate(sections))
        return issues
