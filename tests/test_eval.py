"""Tests for Golden Set evaluation and regression testing framework (Challenge 4)."""

import json

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from pydantic import BaseModel

from promptsight import (
    GoldenSet,
    GoldenSetRunner,
    GoldenTestCase,
    PromptBuilder,
)


class SimpleSentiment(BaseModel):
    sentiment: str
    confidence: float


def test_golden_set_creation_and_runner():
    cases_data = [
        {
            "id": "test_001",
            "input": {"text": "I love this library!"},
            "expected_output": {"sentiment": "positive"},
            "description": "Clear positive sentiment",
        },
        {
            "id": "test_002",
            "input": {"text": "Terrible customer experience."},
            "expected_output": {"sentiment": "negative"},
            "description": "Clear negative sentiment",
        },
    ]

    golden_set = GoldenSet.from_list(cases_data, name="sentiment_tests")
    assert len(golden_set.cases) == 2

    builder = (
        PromptBuilder()
        .role("Sentiment Classifier")
        .task("Classify sentiment")
        .output_schema(SimpleSentiment)
        .inputs(text="Text to analyze")
    )

    # Fake LLM responses matching expectations
    responses = [
        json.dumps({"sentiment": "positive", "confidence": 0.98}),
        json.dumps({"sentiment": "negative", "confidence": 0.95}),
    ]
    fake_llm = FakeListChatModel(responses=responses)
    chain = builder.to_chain(fake_llm, mode="json")

    runner = GoldenSetRunner(chain=chain, golden_set=golden_set)
    report = runner.run()

    assert report.total_cases == 2
    assert report.passed_cases == 2
    assert report.pass_rate == 1.0
    assert report.avg_latency_ms > 0

    markdown_summary = report.summary()
    assert "Golden Set Evaluation Report" in markdown_summary
    assert "100.0%" in markdown_summary
    assert "`test_001`" in markdown_summary
    assert "PASS" in markdown_summary


def test_golden_set_failure_handling():
    case = GoldenTestCase(
        id="fail_001",
        input_variables={"text": "Hello"},
        expected_output={"sentiment": "positive"},
    )
    golden_set = GoldenSet(name="fail_test", cases=[case])

    # Return something mismatching
    fake_llm = FakeListChatModel(responses=[json.dumps({"sentiment": "neutral"})])
    builder = PromptBuilder().role("Test").task("Task").output_schema(SimpleSentiment)
    chain = builder.to_chain(fake_llm, mode="json")

    runner = GoldenSetRunner(chain=chain, golden_set=golden_set)
    report = runner.run()

    assert report.total_cases == 1
    assert report.passed_cases == 0
    assert report.failed_cases == 1
    assert report.pass_rate == 0.0
