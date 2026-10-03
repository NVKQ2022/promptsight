# PromptSections AST & Specification Order

The `PromptSections` dataclass ([`src/promptwright/sections.py`](../../src/promptwright/sections.py)) is the Abstract Syntax Tree (AST) representing an engineered prompt. It models the canonical section sequence defined in [Prompt Engineering Specification §4](../spec.md#4-prompt-construction-standard).

---

## 📐 Canonical Section Ordering

PromptWright renders sections in the exact order proven to maximize LLM compliance:

| Order | Heading | Purpose | Spec Reference |
|---|---|---|---|
| 1 | `# Role & Goal` | Defines agent identity, scope, and target outcome | §4.1 |
| 2 | `# Context` | Authoritative background data wrapped in XML delimiters | §5, §10 |
| 3 | `# Runtime Inputs` | Explicit listing of variables supplied at execution time | §6 |
| 4 | `# Task` | Decomposed step-by-step instructions with clear action verbs | §7, §12 |
| 5 | `# Constraints` | Explicit boundaries, required categories, and non-hallucination rules | §8 |
| 6 | `# Output Format` | Fixed JSON Schema, compact bullet format, or tabular schema | §11 |
| 7 | `# Verification` | Self-check checklist before returning answer | §13 |
| 8 | *Guardrails* | Instructions to treat delimited context strictly as data | §10 |

---

## 📦 Data Models

### 1. `PromptSections`
```python
@dataclass
class PromptSections:
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
```

### 2. `ContextBlock`
Represents an isolated, delimited piece of authoritative context:
```python
@dataclass
class ContextBlock:
    name: str
    content: str
    tag: str = "context"
    treat_as_data: bool = True
```

### 3. `Example`
Represents a few-shot demonstration:
```python
@dataclass
class Example:
    input_text: str
    output_text: str
    description: Optional[str] = None
```
