# ✍️ PromptWright

> **Production-grade, opinionated prompt engineering framework built on top of LangChain.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-core-green.svg)](https://github.com/langchain-ai/langchain)

`promptwright` turns prompt engineering principles into code. Instead of writing brittle natural language strings, developers declare structured prompts with a fluent **Builder + Middleware** pattern that compiles into production-ready LangChain `ChatPromptTemplate` and LCEL runnable sequences.

---

## ✨ Key Features

- **🏛️ Opinionated Prompt Architecture**: Follows standard sections: Role & Goal, Delimited Context, Runtime Inputs, Decomposed Tasks, Explicit Constraints, Deterministic Output Schema, and Self-Check Verification.
- **🔌 Builder + Middleware Hybrid**: Compose prompts with a clean fluent API, while attaching modular middleware for anti-pattern validation, grounding, and XML delimiters.
- **🛡️ Built-in Anti-Pattern Detection**: Catches vague verbs (*"handle"*, *"process"*), decorative roles, ungrounded speculation, missing schemas, and negative-only constraints at compile time.
- **⚡ LangChain Native**: Directly outputs `ChatPromptTemplate` (f-string safe) and binds to any LangChain LLM via LCEL (`to_chain()` supporting `structured`, `pydantic`, `json`, or `raw` modes).
- **🎯 First-Class Presets**: Out-of-the-box, hardened presets for **Structured Data Extraction** and **Classification**.

---

## 📦 Installation

```bash
pip install promptwright
```

Or with `uv`:

```bash
uv add promptwright
```

---

## 🚀 Quickstart

### 1. The Fluent Builder Pattern

```python
from pydantic import BaseModel, Field
from promptwright import PromptBuilder

class CodeReview(BaseModel):
    summary: str = Field(description="High-level summary of review")
    issues_found: int = Field(description="Total count of issues")

prompt = (
    PromptBuilder()
    .role("Senior Security Engineer")
    .goal("review python code for security vulnerabilities")
    .context("Target environment: Python 3.12, Linux production server", tag="env_context")
    .inputs(code="Source code snippet to review")
    .task(
        "Step 1: Parse the provided code.",
        "Step 2: Check for OWASP Top 10 vulnerabilities.",
        "Step 3: Output findings strictly adhering to the schema."
    )
    .constraints(
        "Only report vulnerabilities directly present in the source code.",
        "Do not invent speculative issues."
    )
    .output_schema(CodeReview)
    .verify(
        "Every reported issue cites exact lines",
        "No ungrounded assumptions"
    )
    .build()  # Returns LangChain ChatPromptTemplate
)

# Use with any LangChain LLM
# chain = prompt | llm.with_structured_output(CodeReview)
# result = chain.invoke({"code": "def run(): ..."})
```

---

## 🎯 Prioritized Use Cases

### Use Case 1: Structured Data Extraction

Extract structured entities from raw, unstructured documents without hallucination:

```python
from typing import List, Optional
from pydantic import BaseModel, Field
from promptwright import create_extraction_prompt

class LineItem(BaseModel):
    item_name: str
    price: float

class Invoice(BaseModel):
    vendor: str
    invoice_id: Optional[str] = None
    total_amount: float
    items: List[LineItem] = Field(default_factory=list)

# Pre-engineered prompt with strict grounding & missing-data handling
extraction_builder = create_extraction_prompt(
    schema=Invoice,
    domain="invoice",
    input_variable="invoice_text",
    allow_missing=True,  # Missing fields safely become null rather than hallucinated
)

prompt = extraction_builder.build()
# chain = extraction_builder.to_chain(llm, mode="structured")
# invoice = chain.invoke({"invoice_text": "Acme Corp Invoice #998 Total: $120.00"})
```

### Use Case 2: Classification & Intent Routing

Classify text strictly within an allowed taxonomy with reasoning & evidence citations:

```python
from promptwright import create_classification_prompt

categories = ["billing", "technical_support", "account_access", "other"]

classification_builder = create_classification_prompt(
    categories=categories,
    domain="customer support ticket",
    input_variable="ticket_body",
    fallback_category="other",
)

prompt = classification_builder.build()
# chain = classification_builder.to_chain(llm, mode="structured")
# result = chain.invoke({"ticket_body": "I forgot my password and cannot sign in."})
# result -> DefaultClassificationResult(category='account_access', reasoning=..., evidence_span=...)
```

---

## 🔌 Middleware System

Attach cross-cutting concerns using `.use(middleware)`:

```python
from promptwright import (
    PromptBuilder,
    StrictGroundingMiddleware,
    AutoDelimiterMiddleware,
    AntiPatternValidator,
)

builder = (
    PromptBuilder()
    .role("Data Analyst")
    .task("Analyze the dataset")
    .output_format("JSON")
    .use(StrictGroundingMiddleware(allow_guessing=False)) # Injects non-hallucination rules
    .use(AutoDelimiterMiddleware(default_tag="data"))      # Delimits runtime inputs
    .use(AntiPatternValidator(strict=True))                # Enforces quality gate at compile time
)
```

You can also pass custom functions as middleware:

```python
def add_citation_rule(sections):
    sections.constraints.append("Always cite page or paragraph numbers.")
    return sections

builder.use(add_citation_rule)
```

---

## 🛡️ Anti-Pattern Quality Gate

`promptwright` checks your prompt at build time against common prompt pitfalls:
- ❌ **Vague verbs**: flags `"handle"`, `"process"`, `"deal with"` -> suggests specific verbs like `"extract"`, `"classify"`.
- ❌ **Decorative roles**: flags `"You are an expert"` -> encourages domain-specific roles.
- ❌ **Missing format**: flags absence of an output schema or format specification.
- ❌ **Missing verification**: warns if no self-check checklist is defined.
- ❌ **Negative-only constraints**: warns when prompts only specify what *not* to do instead of stating desired positive behavior.

Run `.validate(strict=True)` to turn warnings into compile-time exceptions.

---

## 🧪 Testing

Run test suite:

```bash
pytest
```

---

## 📄 License

MIT © [NVKQ2022](https://github.com/NVKQ2022)
