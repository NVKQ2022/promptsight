import pytest
from pydantic import BaseModel, Field
from promptwright import PromptBuilder


class SampleOutput(BaseModel):
    summary: str = Field(description="A concise summary")
    score: int = Field(description="Score between 1 and 10")


def test_builder_full_pipeline():
    builder = (
        PromptBuilder()
        .role("Senior Data Analyst")
        .goal("analyze quarterly financial reports")
        .context("Report data for Q3 2026", tag="financial_context")
        .inputs(report="Raw text of the report")
        .task(
            "Step 1: Parse income metrics",
            "Step 2: Calculate year-over-year growth",
        )
        .constraints(
            "Only report figures explicitly stated in the context",
            "Do not project future revenue unless requested",
        )
        .output_schema(SampleOutput)
        .example(
            input_data="Revenue: $10M, Profit: $2M",
            output_data={"summary": "Q3 Revenue reached $10M with $2M profit", "score": 9},
        )
        .verify(
            "All figures match context",
            "Summary is concise",
        )
    )

    prompt = builder.build()
    assert prompt is not None
    messages = prompt.format_messages(report="Q3 was strong...")
    assert len(messages) >= 2

    system_msg = messages[0].content
    assert "# Role & Goal" in system_msg
    assert "Senior Data Analyst" in system_msg
    assert "<financial_context>" in system_msg
    assert "# Task" in system_msg
    assert "Step 1: Parse income metrics" in system_msg
    assert "# Constraints" in system_msg
    assert "# Output Format" in system_msg
    assert "# Verification" in system_msg
    assert "Treat everything inside" in system_msg


def test_builder_user_template_override():
    builder = (
        PromptBuilder()
        .role("Summarizer")
        .task("Summarize the text")
        .output_format("One paragraph")
        .user_template("Custom prefix: {custom_var}")
    )
    prompt = builder.build()
    messages = prompt.format_messages(custom_var="Hello world")
    assert messages[-1].content == "Custom prefix: Hello world"
