"""Example: Classification & Intent Routing using promptwright."""

import json
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from promptwright import create_classification_prompt


def main():
    print("=== Use Case 2: Intent Classification ===\n")

    # 1. Allowed category taxonomy
    categories = [
        "bug_report",
        "billing_inquiry",
        "feature_request",
        "account_access",
        "general_inquiry",
    ]

    # 2. Build classification prompt
    builder = create_classification_prompt(
        categories=categories,
        domain="customer support ticket",
        input_variable="ticket_body",
        fallback_category="general_inquiry",
    )

    prompt = builder.build()

    sample_ticket = "I am locked out of my account because I lost my 2FA phone."

    # 3. Format and inspect prompt
    messages = prompt.format_messages(ticket_body=sample_ticket)
    print("System Prompt Preview:\n")
    print(messages[0].content[:600] + "...\n")

    # 4. Chain execution (simulated with FakeListChatModel)
    fake_output = json.dumps({
        "category": "account_access",
        "reasoning": "The user explicitly states they are locked out due to losing their 2FA device, which directly relates to account access.",
        "evidence_span": "locked out of my account because I lost my 2FA phone",
    })
    llm = FakeListChatModel(responses=[fake_output])

    chain = builder.to_chain(llm, mode="json")
    result = chain.invoke({"ticket_body": sample_ticket})

    print("Classification Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
