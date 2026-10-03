"""Tests for schema optimization modes (Challenge 1: Dual-Schema Token Waste)."""

from pydantic import BaseModel, Field

from promptwright import PromptBuilder


class ComplexDocument(BaseModel):
    title: str = Field(description="Title of the document")
    author: str = Field(description="Author name")
    word_count: int = Field(description="Total word count")
    tags: list[str] = Field(default_factory=list, description="Keywords")


def test_schema_mode_full():
    builder = (
        PromptBuilder().role("Parser").task("Parse doc").output_schema(ComplexDocument, mode="full")
    )
    prompt = builder.build()
    system_text = prompt.messages[0].prompt.template
    assert "```json" in system_text
    assert '"title":' in system_text
    assert '"properties":' in system_text


def test_schema_mode_concise():
    builder = (
        PromptBuilder()
        .role("Parser")
        .task("Parse doc")
        .output_schema(ComplexDocument, mode="concise")
    )
    prompt = builder.build()
    system_text = prompt.messages[0].prompt.template
    assert "```json" not in system_text
    assert "- `title` (string, required)" in system_text
    assert "- `tags` (list[string], optional)" in system_text


def test_schema_mode_tools_only():
    builder = (
        PromptBuilder()
        .role("Parser")
        .task("Parse doc")
        .output_schema(ComplexDocument, mode="tools_only")
    )
    prompt = builder.build()
    system_text = prompt.messages[0].prompt.template
    assert "```json" not in system_text
    assert "Return the structured response matching the tool definition schema." in system_text
