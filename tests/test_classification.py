from promptwright import create_classification_prompt


def test_classification_preset_builds_valid_prompt():
    categories = ["billing", "technical_support", "feature_request", "other"]
    builder = create_classification_prompt(
        categories=categories,
        domain="support ticket",
        input_variable="ticket_content",
        fallback_category="other",
    )

    prompt = builder.build()
    messages = prompt.format_messages(ticket_content="My payment failed with error 402.")

    system_content = messages[0].content
    assert (
        "Support ticket Classification Specialist" in system_content
        or "Support Ticket" in system_content
    )
    assert "`billing`" in system_content
    assert "`technical_support`" in system_content
    assert "Do not invent new categories" in system_content
    assert "assign `other`" in system_content

    user_content = messages[-1].content
    assert "<ticket_content>" in user_content
    assert "My payment failed" in user_content
