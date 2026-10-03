"""Few-shot example management and dynamic selection (PromtEngineering.md §9, Challenge 2)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Protocol, runtime_checkable

from pydantic import BaseModel

try:
    from langchain_core.example_selectors.base import BaseExampleSelector
except ImportError:  # pragma: no cover

    class BaseExampleSelector:  # type: ignore[no-redef]
        pass


@runtime_checkable
class ExampleSelector(Protocol):
    """Protocol for dynamic example selectors."""

    def select_examples(self, input_variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select a list of examples based on the runtime inputs."""
        ...


class ExampleSelectorAdapter(BaseExampleSelector):
    """Adapts any object implementing select_examples into a LangChain BaseExampleSelector."""

    def __init__(self, selector: Any):
        self.selector = selector

    def add_example(self, example: Dict[str, str]) -> Any:
        if hasattr(self.selector, "add_example") and callable(
            getattr(self.selector, "add_example")
        ):
            return self.selector.add_example(example)
        return None

    def select_examples(self, input_variables: Dict[str, Any]) -> List[dict]:
        return self.selector.select_examples(input_variables)


def ensure_base_example_selector(selector: Any) -> BaseExampleSelector:
    """Ensure the selector satisfies LangChain's BaseExampleSelector requirement."""
    if isinstance(selector, BaseExampleSelector):
        return selector
    return ExampleSelectorAdapter(selector)


class StaticExampleSelector(BaseExampleSelector):
    """Simple in-memory example selector that filters or limits examples."""

    def __init__(self, examples: List[Dict[str, Any]], k: int = 3):
        self.examples = examples
        self.k = k

    def add_example(self, example: Dict[str, str]) -> Any:
        self.examples.append(example)

    def select_examples(self, input_variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.examples[: self.k]


def format_example_payload(val: Any) -> str:
    """Format input/output payload for examples."""
    if isinstance(val, BaseModel):
        return val.model_dump_json(indent=2)
    if isinstance(val, (dict, list)):
        return json.dumps(val, indent=2, ensure_ascii=False)
    return str(val)
