# Renderers & Token Optimization

The renderer module ([`src/promptwright/renderers/`](../../src/promptwright/renderers/)) handles compiling `PromptSections` AST into concrete template strings. It decouples formatting concerns from data storage (SRP) and enables custom syntax output (DIP & OCP).

---

## 🎨 `PromptRenderer` Protocol

```python
@runtime_checkable
class PromptRenderer(Protocol):
    def render_system(self, sections: PromptSections) -> str:
        """Render the system prompt message string."""
        ...

    def render_user(self, sections: PromptSections, custom_template: Optional[str] = None) -> str:
        """Render the user prompt message string."""
        ...
```

The default implementation is `MarkdownSectionRenderer`.

---

## ⚡ Dual-Schema Token Optimization

When building structured workflows, repeating a verbose JSON Schema in both the system prompt **and** the LLM tool-calling API wastes tokens and increases latency.

PromptWright solves this with three distinct `SchemaMode` strategies:

### 1. `mode="full"` (Default)
Emits the entire JSON Schema inside the prompt. Essential when using completion models or standard `JsonOutputParser` / `PydanticOutputParser` where the model receives no external tool definitions.

```python
builder.output_schema(Invoice, mode="full")
```
*Output in Prompt:*
```json
{
  "$defs": { ... },
  "properties": { "vendor": { "type": "string" }, ... },
  "required": [ "vendor", "total" ]
}
```

### 2. `mode="concise"`
Generates a compact bullet summary of required and optional fields without verbose JSON schema boilerplate. Saves **~60% of schema tokens** while providing sufficient structure for smart LLMs.

```python
builder.output_schema(Invoice, mode="concise")
```
*Output in Prompt:*
```text
Return ONLY a JSON object containing the following fields:
- `vendor` (string, required) — Vendor name
- `invoice_number` (string, optional) — Reference code
- `total_usd` (number, required) — Total amount in USD
- `items` (list[LineItem], optional)
```

### 3. `mode="tools_only"` (Zero-Duplication for Function Calling)
When using `llm.with_structured_output(Invoice)` or `to_chain(mode="structured")`, the LLM API already receives the schema as an API parameter. This mode completely removes the schema from the prompt text:

```python
builder.output_schema(Invoice, mode="tools_only")
```
*Output in Prompt:*
```text
Return the structured response matching the tool definition schema.
Do not include any prose, markdown explanations, or text outside the structured call.
```

---

## 🛡️ Intelligent Brace Escaping (`escape_fstring_braces`)

LangChain's `template_format="f-string"` evaluates any `{...}` pattern as a template substitution variable. This causes frequent crashes when users write:
- Regex quantifiers: `\d{2,4}`
- Inline JSON examples: `{"status": 200}`
- Code snippets: `def foo(): return {"a": 1}`

PromptWright's escaper ([`src/promptwright/utils/escaping.py`](../../src/promptwright/utils/escaping.py)):
1. Preserves registered input variables (`{invoice_text}`).
2. Preserves already escaped braces (`{{` and `}}`).
3. Automatically doubles unescaped literal braces (`\d{{2,4}}`, `{{"status": 200}}`) so LangChain compiles without error.
