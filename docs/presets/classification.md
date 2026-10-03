# Use Case Preset: Classification & Intent Routing

The classification preset ([`src/promptwright/presets/classification.py`](../../src/promptwright/presets/classification.py)) creates prompts for text classification, intent routing, and categorization with strict taxonomy enforcement.

---

## 🎯 Key Guarantees

1. **Closed Taxonomy Enforcement**: Constrains the LLM to choose strictly from the provided list of categories. Prohibits inventing or altering label names.
2. **Auditable Reasoning & Evidence**: Instructs the model to cite the exact substring from the input that justifies the selected category.
3. **Safe Out-of-Scope Fallback**: Defines an explicit fallback category (e.g. `"other"` or `"unresolved"`) when text does not match any primary category.

---

## 🛠️ Function Signature

```python
def create_classification_prompt(
    categories: List[str],
    *,
    domain: str = "text",
    input_variable: str = "text",
    schema: Optional[Type[BaseModel]] = None,
    allow_unresolved: bool = True,
    fallback_category: str = "other",
) -> PromptBuilder:
```

### Default Output Schema (`DefaultClassificationResult`)
```python
class DefaultClassificationResult(BaseModel):
    category: str = Field(description="The chosen category from allowed taxonomy")
    reasoning: str = Field(description="1-2 sentences justifying the classification")
    evidence_span: Optional[str] = Field(description="Exact quote from input supporting choice")
```

---

## 💻 Complete Example

```python
from promptwright import create_classification_prompt

categories = [
    "bug_report",
    "billing_inquiry",
    "feature_request",
    "account_access",
    "general_inquiry",
]

builder = create_classification_prompt(
    categories=categories,
    domain="customer support ticket",
    input_variable="ticket_content",
    fallback_category="general_inquiry",
)

# Compile to chain
# chain = builder.to_chain(llm, mode="structured")
# result = chain.invoke({"ticket_content": "I was charged twice on my credit card."})
# print(result.category)      -> "billing_inquiry"
# print(result.evidence_span) -> "charged twice on my credit card"
```
