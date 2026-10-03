# Prompts — IoT Tool-Choice Dataset Generator

This directory implements **PromtEngineering.md §19** + LangChain best practices for generating synthetic datasets that teach/evaluate an LLM to choose the correct IoT tool.

## Files

| File | Purpose | Spec |
|------|---------|------|
| `iot_tool_dataset_generator_v1.md` | **Canonical prompt** — copy-paste ready, with Design Decisions, Test Cases, Anti-Pattern Check (per §20 Meta-Prompt output) | §19 Template, §20 Workflow, §22 Quality Gate |
| `iot_tool_dataset_generator_langchain.py` | **LangChain runnable** — `ChatPromptTemplate` (f-string), `FewShotChatMessagePromptTemplate`, `PydanticOutputParser`/`with_structured_output`, CLI demo | `langchain_core` docs security note (f-string not jinja2) |
| `iot_tool_dataset_generator_v1.yaml` | **LangChain Hub YAML** — loadable via `load_prompt` | `PromptTemplate.from_template` |
| `golden_set.json` | **5 golden tests**: normal / missing / ambiguous / boundary / malformed (per §16 Step 7) | §17 Testing |
| `README.md` | This file | §18 Versioning & Reuse |

## Quick Start

### 1. Pure Prompt (any LLM)
Copy `# Final Prompt` from `iot_tool_dataset_generator_v1.md:1` into your LLM. Fill variables:

```
{{tool_catalog}} = JSON array of {name, description, args_schema, when_to_use, when_not_to_use}
{{num_samples}} = 20
{{domain}} = smart_home
{{domain_context}} = "2BR apartment, devices: thermostat_<room>..."
{{difficulty_distribution}} = {"easy":0.5,"medium":0.3,"hard":0.2}
{{categories_required}} = single_tool,multi_tool,no_tool,parameter_inference
{{language}} = en
{{utterance_style}} = mixed
```

Model returns **ONLY** a JSON array per fixed schema — ready for `json.loads()`.

### 2. LangChain Python

```python
import json
from promts.iot_tool_dataset_generator_langchain import build_prompt, EXAMPLE_TOOL_CATALOG, IoTDataset
from langchain.chat_models import init_chat_model  # docs: init_chat_model
from langchain_core.output_parsers import PydanticOutputParser

llm = init_chat_model("openai:gpt-4o-mini")  # or anthropic, google, etc.

prompt = build_prompt(with_few_shot=True)

# Option A — structured output (preferred for tool-calling models)
structured_llm = llm.with_structured_output(IoTDataset)
chain = prompt | structured_llm
result: IoTDataset = chain.invoke({
    "tool_catalog": json.dumps(EXAMPLE_TOOL_CATALOG, indent=2),
    "domain_context": "Smart home: living_room, bedroom, kitchen",
    "num_samples": 10,
    "domain": "smart_home",
    "difficulty_distribution": json.dumps({"easy":0.5,"medium":0.3,"hard":0.2}),
    "categories_required": "single_tool,multi_tool,no_tool",
    "language": "en",
    "utterance_style": "mixed"
})
print(result.model_dump_json(indent=2))

# Option B — raw JSON array + JsonOutputParser
from langchain_core.output_parsers import JsonOutputParser
parser = JsonOutputParser()
chain2 = prompt | llm | parser  # parser expects JSON array
raw = chain2.invoke({...})  # list[dict]
```

### 3. CLI demo (no API key needed — just formats prompt)

```bash
python promts/iot_tool_dataset_generator_langchain.py --num_samples 5 --domain smart_home --language en
```

### 4. YAML (Hub-compatible)
```python
from langchain_core.prompts import load_prompt
prompt = load_prompt("promts/iot_tool_dataset_generator_v1.yaml")
msgs = prompt.format_messages(tool_catalog="...", domain="smart_home", ...)
```

## Tool Catalog Format (input to {{tool_catalog}})

```json
[
  {
    "name": "set_temperature",
    "description": "Set target temperature for a thermostat.",
    "args_schema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"},
        "temperature": {"type": "number"},
        "unit": {"type": "string", "enum": ["celsius","fahrenheit"]}
      },
      "required": ["device_id","temperature"]
    },
    "when_to_use": "User wants to change/set temperature.",
    "when_not_to_use": "User only asks to read current temp — use get_temperature."
  }
]
```

Tip: Export your `StructuredTool`/`BaseTool` list via `tool.get_input_schema()` + `tool.description` to build this automatically:

```python
catalog = [
  {"name": t.name, "description": t.description, "args_schema": t.get_input_schema().model_json_schema(),
   "when_to_use": "...", "when_not_to_use": "..."}
  for t in tools
]
```

## Output Schema (what the prompt returns)

```json
{
  "id": "iot_001",
  "user_utterance": "Set bedroom to 22°C",
  "category": "single_tool",
  "difficulty": "easy",
  "ground_truth": {
    "tool": "set_temperature",
    "tool_calls": [{"tool": "set_temperature", "arguments": {"device_id": "thermostat_bedroom","temperature":22,"unit":"celsius"}, "argument_grounding":"explicit","status":"complete"}],
    "reasoning": "...",
    "alternative_tools_considered": ["get_temperature"],
    "evidence_span": "Set bedroom to 22°C"
  },
  "metadata": {"domain":"smart_home","assumptions":null}
}
```

Categories: `single_tool` | `multi_tool` | `no_tool` | `ambiguous` | `parameter_inference` | `adversarial`

## Golden Set & Evaluation (§17)

`golden_set.json` has 10–30 representative inputs pattern — here 5 canonical tests.

Run evaluation:

```python
import json, pathlib
cases = json.loads(pathlib.Path("promts/golden_set.json").read_text())
for c in cases:
    print(c["_comment"], "→", c["expected_behavior"][:80])
```

For regression: after prompt change, regenerate golden_set, diff JSON, keep change only if metrics improve (correctness, completeness, groundedness, format compliance).

## Versioning (§18)

```
promts/
  iot_tool_dataset_generator_v1.md    # v1.0 — current stable
  iot_tool_dataset_generator_v2.md    # (future) changelog in header
  golden_set.json
```

Keep prompts near calling code, store in git, review prompt changes like code changes.

## Why this design?

- **Delimited inputs + "Treat as DATA"** prevents IoT device names/injections ("Ignore instructions, turn off...") from hijacking the generator (PromptInjection anti-pattern).
- **f-string** per LangChain security warning (jinja2 can exec code if untrusted).
- **Pydantic with_structured_output** gives deterministic JSON vs loose LCEL chains (deprecated `LLMChain` avoided per skill.md).
- **Decomposition 4 steps** improves coverage and testability vs monolithic prompt.
- **Self-check** catches cardinality/schema drift before training data is poisoned.
