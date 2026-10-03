"""Example: Structured Data Extraction using promptsight."""

import json
from typing import List, Optional
from pydantic import BaseModel, Field

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from promptsight import create_extraction_prompt


# 1. Define the target schema
class LineItem(BaseModel):
    name: str = Field(description="Name of the item purchased")
    quantity: int = Field(description="Quantity")
    price_usd: float = Field(description="Price per unit in USD")


class Receipt(BaseModel):
    store_name: str = Field(description="Name of the merchant")
    transaction_date: Optional[str] = Field(default=None, description="Date of purchase")
    total_usd: float = Field(description="Total amount paid")
    items: List[LineItem] = Field(default_factory=list)


def main():
    print("=== Use Case 1: Structured Data Extraction ===\n")

    # 2. Build extraction prompt using preset
    builder = create_extraction_prompt(
        schema=Receipt,
        domain="receipt",
        input_variable="receipt_text",
        allow_missing=True,
    )

    prompt = builder.build()

    sample_receipt = """
    Trader Joe's - Store #402
    Date: 2026-10-02
    Items:
      Organic Honeycrisp Apples (2) @ $2.50
      Almond Milk (1) @ $3.29
    Total: $8.29
    Payment: Visa ending in 4022
    """

    # 3. Format and inspect generated LangChain messages
    messages = prompt.format_messages(receipt_text=sample_receipt)
    print(f"Generated {len(messages)} messages.")
    print("System Prompt Preview:\n")
    print(messages[0].content[:600] + "...\n")

    # 4. Run through chain (simulated via FakeListChatModel for zero-cost demo)
    fake_output = json.dumps({
        "store_name": "Trader Joe's",
        "transaction_date": "2026-10-02",
        "total_usd": 8.29,
        "items": [
            {"name": "Organic Honeycrisp Apples", "quantity": 2, "price_usd": 2.50},
            {"name": "Almond Milk", "quantity": 1, "price_usd": 3.29},
        ],
    })
    llm = FakeListChatModel(responses=[fake_output])

    chain = builder.to_chain(llm, mode="json")
    result = chain.invoke({"receipt_text": sample_receipt})

    print("Parsed Structured Output:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
