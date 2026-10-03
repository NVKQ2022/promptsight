"""Example: Running Golden Set Regression Testing with promptwright."""

import json
from pydantic import BaseModel, Field
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from promptwright import (
    GoldenSet,
    GoldenSetRunner,
    create_extraction_prompt,
)


class ContactCard(BaseModel):
    name: str = Field(description="Full name")
    email: str = Field(description="Email address")
    role: str = Field(description="Job title")


def main():
    print("=== Challenge 4 Demo: Golden Set Evaluation ===\n")

    # 1. Define Golden Test Cases
    test_cases = [
        {
            "id": "contact_001",
            "inputs": {"document": "Alice Smith is our Lead Architect. Reach her at alice@example.com."},
            "expected_output": {
                "name": "Alice Smith",
                "email": "alice@example.com",
                "role": "Lead Architect",
            },
            "description": "Standard contact card extraction",
        },
        {
            "id": "contact_002",
            "inputs": {"document": "Contact Bob Jones (bob@acme.org), VP of Engineering."},
            "expected_output": {
                "name": "Bob Jones",
                "email": "bob@acme.org",
                "role": "VP of Engineering",
            },
            "description": "Parenthesized email address",
        },
    ]

    golden_set = GoldenSet.from_list(test_cases, name="contact_extraction_v1")

    # 2. Build prompt using preset
    builder = create_extraction_prompt(
        schema=ContactCard,
        domain="contact card",
        input_variable="document",
    )

    # 3. Simulated chain (or replace with live ChatOpenAI / ChatAnthropic)
    responses = [
        json.dumps({"name": "Alice Smith", "email": "alice@example.com", "role": "Lead Architect"}),
        json.dumps({"name": "Bob Jones", "email": "bob@acme.org", "role": "VP of Engineering"}),
    ]
    fake_llm = FakeListChatModel(responses=responses)
    chain = builder.to_chain(fake_llm, mode="json")

    # 4. Run Golden Set Evaluation
    runner = GoldenSetRunner(chain=chain, golden_set=golden_set)
    report = runner.run()

    # 5. Print summary
    print(report.summary())


if __name__ == "__main__":
    main()
