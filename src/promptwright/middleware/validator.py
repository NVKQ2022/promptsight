"""Anti-pattern detection and Quality Gate validator middleware (PromtEngineering.md §15, §22)."""

from __future__ import annotations

import re
from typing import List, Optional

from promptwright.middleware.base import BaseMiddleware, IssueSeverity, ValidationIssue
from promptwright.sections import PromptSections


VAGUE_VERBS = {
    "handle",
    "deal with",
    "process",
    "work on",
    "take care of",
    "manage",
    "look at",
}

DECORATIVE_ROLES = {
    "an expert",
    "expert",
    "helpful assistant",
    "assistant",
    "ai assistant",
    "an ai",
    "ai",
}


class AntiPatternValidator(BaseMiddleware):
    """Checks prompts for common anti-patterns (§15) and Quality Gate (§22)."""

    def __init__(self, strict: bool = False):
        self.strict = strict

    def validate(self, sections: PromptSections) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        # 1. Check Role & Goal
        if not sections.role and not sections.goal:
            issues.append(
                ValidationIssue(
                    code="MISSING_ROLE_AND_GOAL",
                    section="role_goal",
                    message="Neither role nor goal is specified.",
                    severity=IssueSeverity.WARNING,
                    suggestion="Specify who the model is (.role()) and the target outcome (.goal()).",
                )
            )
        elif sections.role:
            cleaned_role = sections.role.strip().lower()
            if cleaned_role in DECORATIVE_ROLES:
                issues.append(
                    ValidationIssue(
                        code="DECORATIVE_ROLE",
                        section="role",
                        message=f"Role '{sections.role}' appears decorative and adds little guidance.",
                        severity=IssueSeverity.WARNING,
                        suggestion="Use a specific domain role (e.g., 'Senior QA Engineer', 'Invoice Parser').",
                    )
                )

        # 2. Check Tasks & Vague Verbs
        if not sections.tasks:
            issues.append(
                ValidationIssue(
                    code="MISSING_TASK",
                    section="task",
                    message="No explicit task was specified.",
                    severity=IssueSeverity.ERROR,
                    suggestion="Add at least one clear primary task instruction via .task().",
                )
            )
        else:
            for task in sections.tasks:
                task_lower = task.lower()
                for vague in VAGUE_VERBS:
                    pattern = rf"\b{re.escape(vague)}\b"
                    if re.search(pattern, task_lower):
                        issues.append(
                            ValidationIssue(
                                code="VAGUE_VERB",
                                section="task",
                                message=f"Task uses vague verb '{vague}': \"{task}\"",
                                severity=IssueSeverity.WARNING,
                                suggestion="Replace with precise action verbs (extract, classify, compare, summarize, validate, generate).",
                            )
                        )

        # 3. Check Output Format / Schema (§11)
        if not sections.output_schema and not sections.output_format_text:
            issues.append(
                ValidationIssue(
                    code="MISSING_OUTPUT_FORMAT",
                    section="output_format",
                    message="No fixed output schema or format was defined.",
                    severity=IssueSeverity.WARNING,
                    suggestion="Provide a Pydantic model via .output_schema() or format description via .output_format().",
                )
            )

        # 4. Check Negative-Only Constraints (§8, §15)
        if sections.constraints:
            negative_prefixes = ("do not", "don't", "never", "cannot")
            all_negative = all(
                c.strip().lower().startswith(negative_prefixes) for c in sections.constraints
            )
            if all_negative and len(sections.constraints) >= 2:
                issues.append(
                    ValidationIssue(
                        code="NEGATIVE_ONLY_CONSTRAINTS",
                        section="constraints",
                        message="All constraints are negative prohibitions ('do not', 'never').",
                        severity=IssueSeverity.WARNING,
                        suggestion="State desired positive behavior directly rather than relying solely on prohibitions.",
                    )
                )

        # 5. Check Verification Checklist (§13, §22)
        if not sections.verifications:
            issues.append(
                ValidationIssue(
                    code="MISSING_VERIFICATION",
                    section="verification",
                    message="No verification checklist items specified.",
                    severity=IssueSeverity.WARNING,
                    suggestion="Add a self-check checklist via .verify('item 1', 'item 2').",
                )
            )

        return issues
