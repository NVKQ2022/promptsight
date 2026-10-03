# PromptBuilder API Reference

The `PromptBuilder` class ([`src/promptsight/builder.py`](../../src/promptsight/builder.py)) provides a fluent builder pattern for authoring production-grade LangChain prompts.

---

## 📋 Method Reference

### 1. Identity & Objective
* **`.role(role: str) -> PromptBuilder`**
  Specifies who the model is (e.g. `"Senior QA Automation Engineer"`). Flags decorative roles like `"an expert"` during validation.
* **`.goal(goal: str) -> PromptBuilder`**
  Specifies the target business outcome (e.g. `"produce a test-case matrix derived solely from acceptance criteria"`).

### 2. Context & Runtime Inputs
* **`.context(content: str, tag: str = "context", name: str = "", treat_as_data: bool = True) -> PromptBuilder`**
  Adds an authoritative background knowledge block enclosed in XML delimiters (e.g. `<context>...</context>`). When `treat_as_data=True`, appends prompt injection guardrails instructing the LLM to treat the content as passive data.
* **`.inputs(*names: str, **named_inputs: str) -> PromptBuilder`**
  Registers runtime variable names and their descriptions. These variables are automatically preserved during template brace escaping and formatted into the user prompt.

### 3. Task & Instructions
* **`.task(*steps: str) -> PromptBuilder`**
  Defines the primary task. If multiple steps are passed, they are automatically numbered as `Step 1: ...`, `Step 2: ...` per decomposition principles (§12).
* **`.constraints(*rules: str) -> PromptBuilder`**
  Defines explicit limits, required categories, length boundaries, and non-hallucination guardrails (§8).

### 4. Deterministic Output Shape
* **`.output_schema(schema: Type[BaseModel], mode: Literal["full", "concise", "tools_only"] = "full") -> PromptBuilder`**
  Binds a Pydantic model to define the expected response shape.
  - `mode="full"`: Injects the complete JSON Schema into prompt text (standard for JSON output parsers).
  - `mode="concise"`: Injects a compact summary of field names, types, and descriptions (~60% token savings).
  - `mode="tools_only"`: Injects only a brief reference, leaving the schema definition to the model's function-calling tool API (zero token duplication).
* **`.output_format(text: str) -> PromptBuilder`**
  Sets a custom output structure description (tables, fixed headings, or text schemas).

### 5. Few-Shot Examples
* **`.example(input_data: Any, output_data: Any, description: Optional[str] = None) -> PromptBuilder`**
  Appends an in-memory input/output example. Automatically formats Pydantic models, dicts, or strings into JSON.
* **`.example_selector(selector: Any, example_prompt: Optional[ChatPromptTemplate] = None) -> PromptBuilder`**
  Attaches a dynamic example selector (such as LangChain's `SemanticSimilarityExampleSelector` or custom implementations) for vectorstore-based few-shot retrieval.

### 6. Verification Checklist
* **`.verify(*checklist_items: str) -> PromptBuilder`**
  Appends self-check verification items (`- [ ] ...`) instructing the model to audit its answer before returning it (§13).

### 7. Customization & Middleware
* **`.use(component: PipelineComponent) -> PromptBuilder`**
  Registers a transformer, validator, or callable middleware plugin.
* **`.with_renderer(renderer: PromptRenderer) -> PromptBuilder`**
  Injects an alternative prompt renderer (e.g. XML, YAML).
* **`.user_template(template: str) -> PromptBuilder`**
  Overrides the default user message template.

### 8. Compilation & Chain Execution
* **`.validate(strict: bool = False) -> List[ValidationIssue]`**
  Audits the prompt against §15 Anti-Patterns. If `strict=True`, raises `ValueError` on any error-level violation.
* **`.build(strict: bool = False, with_few_shot: bool = True) -> ChatPromptTemplate`**
  Compiles the prompt into a secure LangChain `ChatPromptTemplate` (f-string format).
* **`.to_chain(llm: Any, mode: str = "structured", strict: bool = False) -> RunnableSequence`**
  Compiles the prompt and binds directly to the LLM via LangChain LCEL. Supported modes: `"structured"`, `"pydantic"`, `"json"`, `"raw"`.

---

## 💻 Full Code Example

```python
from pydantic import BaseModel, Field
from promptsight import PromptBuilder

class RiskAssessment(BaseModel):
    risk_level: str = Field(description="low, medium, high, critical")
    summary: str = Field(description="Summary of risk factors")
    mitigation_steps: list[str] = Field(description="Recommended steps")

builder = (
    PromptBuilder()
    .role("Senior Site Reliability Engineer")
    .goal("assess deployment risk for upcoming infrastructure change")
    .context("Infrastructure: AWS EKS, PostgreSQL 16 on Aurora", tag="infra_specs")
    .inputs(change_log="The pull request description and commit diff")
    .task(
        "Step 1: Parse the change log for schema migrations and infrastructure updates.",
        "Step 2: Identify single points of failure.",
        "Step 3: Return the risk evaluation adhering strictly to the schema.",
    )
    .constraints(
        "Base assessment solely on the supplied change log and infra specs.",
        "Do not invent hypothetical dependencies.",
    )
    .output_schema(RiskAssessment, mode="tools_only")
    .verify(
        "Every identified risk cites specific lines from change_log",
        "Risk level matches stated criteria",
    )
)

# 1. Compile to ChatPromptTemplate
prompt = builder.build()

# 2. Bind directly to LLM LCEL Chain
chain = builder.to_chain(llm, mode="structured")
result = chain.invoke({"change_log": "PR #402: Add index on users(email)..."})
```
