# Middleware & Quality Gate Architecture

The middleware architecture in PromptWright ([`src/promptwright/middleware/`](../../src/promptwright/middleware/)) enables cross-cutting concerns—such as compile-time linting, non-hallucination guardrail injection, and XML wrapping—without polluting the core builder.

---

## 🔌 Segregated Protocols (Interface Segregation Principle)

PromptWright splits middleware into two granular protocols:

```python
@runtime_checkable
class SectionTransformer(Protocol):
    """Transforms or enriches sections before rendering."""
    def transform(self, sections: PromptSections) -> PromptSections:
        ...

@runtime_checkable
class PromptValidator(Protocol):
    """Audits sections against rules or anti-patterns."""
    def validate(self, sections: PromptSections) -> List[ValidationIssue]:
        ...
```

You can pass a pure transformer, a pure validator, a composite middleware, or a standard Python function into `.use(...)`.

---

## 🛡️ Built-in Anti-Pattern Rules (PromtEngineering.md §15)

PromptWright evaluates prompts against common prompt engineering anti-patterns before compilation:

| Rule Class | Code | What It Catches | Recommendation / Fix |
|---|---|---|---|
| `RoleAndGoalRule` | `MISSING_ROLE_AND_GOAL` | Neither role nor goal specified | Define role and outcome |
| `RoleAndGoalRule` | `DECORATIVE_ROLE` | Decorative roles like `"an expert"`, `"helpful assistant"` | Use domain role (e.g. `"Senior Tax Auditor"`) |
| `TaskClarityRule` | `MISSING_TASK` | No task instructions defined | Add clear task via `.task()` |
| `TaskClarityRule` | `VAGUE_VERB` | Vague verbs: `"handle"`, `"process"`, `"deal with"`, `"manage"` | Replace with action verbs: `"extract"`, `"classify"`, `"summarize"` |
| `OutputFormatRule` | `MISSING_OUTPUT_FORMAT` | Neither schema nor format defined | Provide `.output_schema()` or `.output_format()` |
| `ConstraintsStyleRule` | `NEGATIVE_ONLY_CONSTRAINTS` | Prompts using only prohibitions (`"do not"`, `"never"`) | Reframe into desired positive behavior |
| `VerificationChecklistRule` | `MISSING_VERIFICATION` | No self-check verification items | Add checklist via `.verify(...)` |

### Strict vs Non-Strict Validation
```python
# Non-strict (default): logs issues or inspects via builder.validate()
issues = builder.validate(strict=False)

# Strict: raises ValueError on ERROR severity violations
builder.build(strict=True)
```

---

## 🔒 Built-in Transformers

### 1. `StrictGroundingMiddleware`
Implements [PromtEngineering.md §14](../../PromtEngineering.md#14-handling-ambiguity-and-missing-information):
- Automatically injects non-hallucination constraints:
  *"Use only information directly supported by the provided context."*
- Handles missing data explicitly:
  *"If required information is missing or ambiguous, mark as null/unknown. Do not invent or guess facts."*
- Injects verification self-check item.

```python
from promptwright import StrictGroundingMiddleware

builder.use(StrictGroundingMiddleware(allow_guessing=False))
```

### 2. `AutoDelimiterMiddleware`
Implements [PromtEngineering.md §10](../../PromtEngineering.md#10-delimit-inputs):
- Automatically verifies and wraps context in appropriate tags (`<context>`, `<document>`).
- Appends prompt-injection guardrails instructing the model to treat content strictly as passive data.

```python
from promptwright import AutoDelimiterMiddleware

builder.use(AutoDelimiterMiddleware(default_tag="document"))
```

---

## ✍️ Writing Custom Middleware

### Method 1: Using a Simple Function
```python
def add_citation_rule(sections: PromptSections) -> PromptSections:
    sections.constraints.append("Every claim must cite paragraph number.")
    return sections

builder.use(add_citation_rule)
```

### Method 2: Implementing a Class
```python
from promptwright import ValidationIssue, ValidationRule

class MaxTaskStepsRule(ValidationRule):
    def evaluate(self, sections: PromptSections) -> list[ValidationIssue]:
        if len(sections.tasks) > 7:
            return [
                ValidationIssue(
                    code="OVERLOADED_TASK",
                    section="task",
                    message=f"Prompt has {len(sections.tasks)} steps. Decompose into multiple chains.",
                )
            ]
        return []

custom_validator = AntiPatternValidator(rules=[MaxTaskStepsRule()])
builder.use(custom_validator)
```
