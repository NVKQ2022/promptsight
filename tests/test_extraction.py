import pytest
from typing import List, Optional
from pydantic import BaseModel, Field
from promptwright import create_extraction_prompt


class LineItem(BaseModel):
    description: str
    amount: float


class Invoice(BaseModel):
    vendor: str = Field(description="Vendor or company name")
    invoice_number: Optional[str] = Field(default=None, description="Invoice reference code")
    total_usd: float = Field(description="Total invoice amount in USD")
    items: List[LineItem] = Field(default_factory=list)


def test_extraction_preset_builds_valid_prompt():
    builder = create_extraction_prompt(
        schema=Invoice,
        domain="invoice",
        input_variable="invoice_text",
    )
    prompt = builder.build()
    messages = prompt.format_messages(invoice_text="Acme Corp Invoice #123 Total: $500.00")

    system_content = messages[0].content
    assert "Information Extraction Specialist" in system_content
    assert "Invoice" in system_content
    assert "Do not extrapolate, assume, or fabricate" in system_content
    assert "null" in system_content.lower()

    user_content = messages[-1].content
    assert "<invoice_text>" in user_content
    assert "Acme Corp Invoice #123" in user_content
