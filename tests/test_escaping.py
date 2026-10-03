"""Tests for intelligent f-string template brace escaping (Challenge 3)."""

from promptsight import PromptBuilder
from promptsight.utils.escaping import escape_fstring_braces


def test_escape_fstring_braces_preserves_allowed_vars():
    raw = "Extract regex \\d{2,4} from {query} and return JSON {'res': 1}."
    escaped = escape_fstring_braces(raw, allowed_variables={"query"})

    assert "\\d{{2,4}}" in escaped
    assert "{query}" in escaped  # kept as valid variable
    assert "{{'res': 1}}" in escaped


def test_builder_with_complex_code_and_regex():
    builder = (
        PromptBuilder()
        .role("Regex and Code Parser")
        .inputs(code_snippet="Raw code to parse")
        .task(
            "Step 1: Check pattern match ^[a-z]{3,5}$ against input.",
            "Step 2: Return dictionary {'matched': True, 'count': 1}.",
        )
        .constraints(
            "Do not alter regex bounds {3,5}.",
        )
        .output_format("JSON dictionary")
    )

    prompt = builder.build()
    # Must format cleanly without KeyError or ValueError from LangChain f-string parser
    messages = prompt.format_messages(code_snippet="abc")
    assert len(messages) >= 2
    system_text = messages[0].content
    assert "^[a-z]{3,5}$" in system_text
    assert "{'matched': True, 'count': 1}" in system_text
    assert "{3,5}" in system_text
