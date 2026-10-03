# AI Prompt Generator (Meta-Prompting)

The AI prompt generation module ([`src/promptwright/meta/`](../../src/promptwright/meta/)) implements **[PromtEngineering.md §20 (Meta-Prompt for an AI Agent)](../../PromtEngineering.md#20-meta-prompt-for-an-ai-agent)**. It uses a LangChain LLM to design production-quality prompts from raw user task descriptions.

---

## 🎯 What It Does

Instead of writing prompts manually from scratch, developers can supply a natural language goal. PromptWright's meta-prompting engine:
1. Assigns a specific domain role (rejecting generic roles like *"an expert"*).
2. Decomposes tasks into numbered steps with precise action verbs (rejecting vague verbs like *"handle"* or *"process"*).
3. Defines explicit constraints and safe fallbacks for missing/ambiguous data (`null` / `"unresolved"`).
4. Generates realistic few-shot demonstrations and self-check verification checklists.
5. Returns a structured `GeneratedPromptSpec` that can be exported to **Markdown** or converted directly into an executable **`PromptBuilder`**.

---

## 🚀 Quick Example

```python
from langchain_openai import ChatOpenAI
from promptwright import generate_prompt_from_task

llm = ChatOpenAI(model="gpt-4o")

# 1. Ask LLM to engineer a prompt from a raw task request
spec = generate_prompt_from_task(
    user_task="I want a prompt to extract invoices from emails, pull out line items, and flag overdue balances.",
    llm=llm,
    additional_context="Domain: Commercial accounting.",
)

# 2. Inspect the prompt as clean Markdown (§19)
print(spec.to_markdown())

# 3. View the AI Prompt Engineer's rationale and test cases (§20)
print(spec.design_decisions)
print(spec.test_cases)
print(spec.anti_patterns_avoided)

# 4. Convert directly to a live LangChain PromptBuilder
builder = spec.to_builder()
prompt = builder.build()
chain = builder.to_chain(llm, mode="structured")
```

---

## 📦 `GeneratedPromptSpec` Reference

The `GeneratedPromptSpec` model contains:

| Field | Type | Description |
|---|---|---|
| `role` | `str` | Domain-specific role (e.g. `"Senior Accounting Auditor"`) |
| `goal` | `str` | Explicit desired outcome |
| `context_data` | `Optional[str]` | Static background rules or definitions |
| `inputs` | `Dict[str, str]` | Runtime input variables and their descriptions |
| `tasks` | `List[str]` | Decomposed instructions with precise action verbs |
| `constraints` | `List[str]` | Explicit boundaries and missing-data fallbacks |
| `output_format` | `str` | Fixed JSON schema, markdown table, or text structure |
| `examples` | `List[GeneratedExample]` | Few-shot input/output demonstrations |
| `verifications` | `List[str]` | Self-check verification checklist items |
| `design_decisions` | `Optional[str]` | Architectural rationale (§20) |
| `test_cases` | `List[str]` | 5 representative edge test cases (§20) |
| `anti_patterns_avoided`| `List[str]` | Checklist of detected & resolved anti-patterns |

### Methods
- **`.to_builder() -> PromptBuilder`**: Instantiates a live `PromptBuilder` ready for `.build()` or `.to_chain(llm)`.
- **`.to_markdown() -> str`**: Renders the complete prompt ready for copy-pasting or file storage.
