"""Tests for AI Prompt Generation / Meta-Prompting (docs/spec.md §20)."""

import json

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from promptsight import (
    GeneratedPromptSpec,
    generate_prompt_from_task,
)
from promptsight.meta.models import GeneratedExample


def test_generated_prompt_spec_to_builder_and_markdown():
    spec = GeneratedPromptSpec(
        role="Senior QA Test Engineer",
        goal="generate comprehensive test cases from user stories",
        context_data="System: Microservices banking backend",
        inputs={"user_story": "Raw user story text"},
        tasks=[
            "Step 1: Extract all acceptance criteria from the story.",
            "Step 2: Generate positive, negative, and edge test cases.",
        ],
        constraints=[
            "Base test cases solely on supplied acceptance criteria.",
            "Do not invent unspecified criteria.",
        ],
        output_format="Return a markdown table of test cases.",
        examples=[
            GeneratedExample(
                input_text="Story: As a user, I want to login with email.",
                output_text="| TC-01 | Valid email | Positive |",
                description="Simple login case",
            )
        ],
        verifications=[
            "Every acceptance criterion has at least 2 test cases",
            "No invented assumptions",
        ],
        design_decisions="Chose tabular output for QA readability.",
        test_cases=["Normal valid story", "Missing acceptance criteria"],
        anti_patterns_avoided=["Vague verbs eliminated"],
    )

    # 1. Test markdown rendering
    md = spec.to_markdown()
    assert "# Role & Goal" in md
    assert "Senior QA Test Engineer" in md
    assert "# Context" in md
    assert "<context>" in md
    assert "Microservices banking backend" in md
    assert "# Task" in md
    assert "Step 1: Extract" in md
    assert "# Constraints" in md
    assert "# Examples" in md
    assert "TC-01" in md
    assert "# Verification" in md

    # 2. Test conversion to live PromptBuilder
    builder = spec.to_builder()
    prompt = builder.build()
    messages = prompt.format_messages(user_story="As a shopper, I want to checkout.")

    assert len(messages) >= 2
    system_text = messages[0].content
    assert "Senior QA Test Engineer" in system_text
    assert "Microservices banking backend" in system_text
    assert "Step 1: Extract" in system_text

    user_text = messages[-1].content
    assert "<user_story>" in user_text
    assert "As a shopper" in user_text


def test_ai_prompt_generator_with_fake_llm():
    mock_payload = {
        "role": "Customer Feedback Sentiment Analyst",
        "goal": "extract sentiment and feature requests from reviews",
        "inputs": {"review_text": "Raw user review"},
        "tasks": [
            "Step 1: Read the customer review thoroughly.",
            "Step 2: Classify sentiment as positive, neutral, or negative.",
            "Step 3: Extract any actionable feature requests.",
        ],
        "constraints": [
            "Do not invent feedback not present in the review.",
            "If no feature request is mentioned, set feature_requests to empty list.",
        ],
        "output_format": "JSON with sentiment and feature_requests fields.",
        "examples": [
            {
                "input_text": "Great app, but please add dark mode!",
                "output_text": '{"sentiment": "positive", "feature_requests": ["dark mode"]}',
                "description": "Positive review with feature request",
            }
        ],
        "verifications": [
            "Sentiment is one of allowed values",
            "Extracted requests are directly quoted",
        ],
        "design_decisions": "Decomposed into 3 clear steps with non-hallucination constraints.",
        "test_cases": ["Positive review", "Empty review", "Bug report review"],
        "anti_patterns_avoided": ["Eliminated vague verbs 'handle feedback'"],
    }

    fake_llm = FakeListChatModel(responses=[json.dumps(mock_payload)])

    spec = generate_prompt_from_task(
        user_task="I want an assistant to analyze customer feedback and pull out feature ideas.",
        llm=fake_llm,
        additional_context="Target domain: Mobile E-commerce App",
    )

    assert isinstance(spec, GeneratedPromptSpec)
    assert spec.role == "Customer Feedback Sentiment Analyst"
    assert len(spec.tasks) == 3
    assert "review_text" in spec.inputs

    # Verify builder converts cleanly
    builder = spec.to_builder()
    prompt = builder.build()
    messages = prompt.format_messages(review_text="Love the checkout flow!")
    assert len(messages) >= 2
    assert "Sentiment Analyst" in messages[0].content
