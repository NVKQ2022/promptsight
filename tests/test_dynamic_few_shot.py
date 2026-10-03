"""Tests for dynamic few-shot example selection (Challenge 2)."""

from promptwright import ExampleSelector, PromptBuilder


class QueryMatchingSelector(ExampleSelector):
    """Dynamic selector picking examples matching the domain keyword."""

    def __init__(self, examples: list[dict]):
        self.examples = examples

    def select_examples(self, input_variables: dict) -> list[dict]:
        query = input_variables.get("input", "").lower()
        if "math" in query:
            return [ex for ex in self.examples if "math" in ex["input"].lower()]
        return [ex for ex in self.examples if "code" in ex["input"].lower()]


def test_dynamic_example_selector():
    example_bank = [
        {"input": "Solve math: 2+2", "output": "4"},
        {"input": "Solve math: 3*3", "output": "9"},
        {"input": "Write code: print hello", "output": "print('hello')"},
    ]

    selector = QueryMatchingSelector(example_bank)

    builder = (
        PromptBuilder()
        .role("Assistant")
        .task("Answer user question")
        .inputs(input="User query")
        .example_selector(selector)
    )

    prompt = builder.build()

    # Query 1: math
    math_messages = prompt.format_messages(input="Solve math: 10/2")
    # Should include only math examples
    assert any("2+2" in m.content for m in math_messages)
    assert not any("print('hello')" in m.content for m in math_messages)

    # Query 2: code
    code_messages = prompt.format_messages(input="Write code: loop 5 times")
    assert any("print('hello')" in m.content for m in code_messages)
    assert not any("2+2" in m.content for m in code_messages)
