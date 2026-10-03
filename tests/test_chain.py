import json
import pytest
from pydantic import BaseModel
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from promptwright import PromptBuilder


class SentimentResult(BaseModel):
    sentiment: str
    confidence: float


def test_chain_execution_json_mode():
    builder = (
        PromptBuilder()
        .role("Sentiment Classifier")
        .task("Classify sentiment")
        .output_schema(SentimentResult)
        .inputs(text="Text to analyze")
    )

    fake_response = json.dumps({"sentiment": "positive", "confidence": 0.95})
    fake_llm = FakeListChatModel(responses=[fake_response])

    chain = builder.to_chain(fake_llm, mode="json")
    result = chain.invoke({"text": "I love this library!"})

    assert isinstance(result, dict)
    assert result["sentiment"] == "positive"
    assert result["confidence"] == 0.95


def test_chain_execution_raw_mode():
    builder = (
        PromptBuilder()
        .role("Echo")
        .task("Echo the input")
        .inputs(text="Input text")
    )
    fake_llm = FakeListChatModel(responses=["Echo: Hello"])
    chain = builder.to_chain(fake_llm, mode="raw")
    result = chain.invoke({"text": "Hello"})
    assert result == "Echo: Hello"
