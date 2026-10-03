# Golden Set Evaluation & Regression Testing

The evaluation module ([`src/promptsight/eval/`](../../src/promptsight/eval/)) directly implements **[Prompt Engineering Specification §17](../spec.md#17-prompt-testing-and-evaluation)**. It treats prompts as versioned code artifacts and automates regression benchmarking.

---

## 🎯 The Golden Set Philosophy

Prompts generate probabilistic outputs. Unit tests verify that the Python code runs, but a **Golden Set** verifies that the LLM continues to satisfy accuracy, schema compliance, and groundedness across versions.

A recommended golden set contains **10–30 representative inputs** covering:
1. Normal valid input
2. Missing information
3. Ambiguous input
4. Boundary / edge case
5. Unexpected or malformed input

---

## 📦 Defining a Golden Set

Golden sets can be defined in Python code, JSON files, or YAML files:

### `golden_set.json`
```json
[
  {
    "id": "tc_001",
    "inputs": {"document": "Invoice #402 from Acme Corp Total: $500.00"},
    "expected_output": {"vendor": "Acme Corp", "total": 500.0},
    "description": "Standard invoice parsing"
  },
  {
    "id": "tc_002",
    "inputs": {"document": "Receipt without date Total: $12.50"},
    "expected_output": {"vendor": "unknown", "total": 12.5},
    "description": "Missing vendor handling"
  }
]
```

### Loading in Python
```python
from promptsight import GoldenSet

golden_set = GoldenSet.from_file("golden_set.json")
```

---

## 🚀 Running Benchmarks with `GoldenSetRunner`

```python
from promptsight import GoldenSet, GoldenSetRunner, SchemaComplianceEvaluator, FieldMatchEvaluator

# 1. Initialize runner
runner = GoldenSetRunner(
    chain=my_lcel_chain,
    golden_set=golden_set,
    evaluators=[
        SchemaComplianceEvaluator(schema=Invoice),
        FieldMatchEvaluator(key_fields=["vendor", "total"]),
    ],
)

# 2. Execute all test cases
report = runner.run()

# 3. Print markdown summary
print(report.summary())
```

---

## 📊 Sample CI/CD Markdown Output

The `report.summary()` method generates formatted Markdown tables ready for GitHub Actions step summaries, PR comments, or terminal logs:

```markdown
## ✅ Golden Set Evaluation Report: `invoice_extraction_v1`

- **Pass Rate**: 100.0% (2/2 passed)
- **Average Latency**: 4.6 ms

| Case ID | Status | Score | Latency | Error / Notes |
|---|---|---|---|---|
| `tc_001` | PASS | 1.00 | 8 ms | - |
| `tc_002` | PASS | 1.00 | 1 ms | - |
```

---

## 🔍 Built-in Evaluators

1. **`SchemaComplianceEvaluator`**: Validates whether actual output can be parsed by the target Pydantic model.
2. **`FieldMatchEvaluator`**: Compares designated dictionary keys between expected and actual outputs with case-insensitive normalization.
3. **`CustomFunctionEvaluator`**: Allows developers to inject custom scoring functions `(case, actual_output) -> (passed, score, details)`.
