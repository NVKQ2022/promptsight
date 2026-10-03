# Use Case Preset: Structured Data Extraction

The extraction preset ([`src/promptwright/presets/extraction.py`](../../src/promptwright/presets/extraction.py)) provides a production-hardened prompt for extracting structured data from unstructured text without hallucination.

---

## 🎯 Key Guarantees

1. **Zero Hallucination / Strict Grounding**: Injects constraints requiring every extracted value to be directly supported by evidence in the source text.
2. **Explicit Missing-Data Behavior**: When optional fields are omitted from source text, instructs the model to return `null` rather than inventing plausible values.
3. **Data Type Normalization**: Explicitly instructs the model to cast dates, floats, and ints according to the Pydantic schema types.
4. **Injection Guard**: Wraps input documents in XML delimiters (`<document>...</document>`) with instructions to treat them strictly as data.

---

## 🛠️ Function Signature

```python
def create_extraction_prompt(
    schema: Type[BaseModel],
    *,
    domain: str = "document",
    input_variable: str = "document",
    role: Optional[str] = None,
    allow_missing: bool = True,
) -> PromptBuilder:
```

---

## 💻 Complete Example

```python
from typing import List, Optional
from pydantic import BaseModel, Field
from promptwright import create_extraction_prompt

# 1. Define the schema
class LineItem(BaseModel):
    name: str = Field(description="Item description")
    quantity: int = Field(description="Quantity purchased")
    unit_price_usd: float = Field(description="Price per unit in USD")

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the selling vendor")
    invoice_number: Optional[str] = Field(default=None, description="Invoice reference ID")
    total_amount_usd: float = Field(description="Total amount due")
    items: List[LineItem] = Field(default_factory=list)

# 2. Build extraction prompt
builder = create_extraction_prompt(
    schema=Invoice,
    domain="invoice",
    input_variable="invoice_text",
    allow_missing=True,
)

# 3. Compile and execute
# chain = builder.to_chain(llm, mode="structured")
# invoice: Invoice = chain.invoke({"invoice_text": raw_invoice_ocr_string})
```
