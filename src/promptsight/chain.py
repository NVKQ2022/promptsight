"""Strategy pattern for LCEL chain construction (OCP & DIP)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, Type, Union, runtime_checkable

from pydantic import BaseModel

try:
    from langchain_core.output_parsers import (
        JsonOutputParser,
        PydanticOutputParser,
        StrOutputParser,
    )
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableSequence
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "langchain-core is required to build chains. Install with: pip install langchain-core"
    ) from e


@runtime_checkable
class ChainStrategy(Protocol):
    """Protocol for LCEL chain building strategies (OCP & DIP)."""

    def build(
        self,
        prompt: ChatPromptTemplate,
        llm: Any,
        schema: Optional[Type[BaseModel]] = None,
    ) -> RunnableSequence: ...


class StructuredChainStrategy:
    """Uses llm.with_structured_output(schema) for function/tool-calling models."""

    def build(
        self,
        prompt: ChatPromptTemplate,
        llm: Any,
        schema: Optional[Type[BaseModel]] = None,
    ) -> RunnableSequence:
        if schema is None:
            raise ValueError("StructuredChainStrategy requires a Pydantic schema class.")
        if not hasattr(llm, "with_structured_output"):
            raise ValueError(
                f"LLM {type(llm)} does not implement with_structured_output(). "
                "Use 'pydantic' or 'json' mode instead."
            )
        structured_llm = llm.with_structured_output(schema)
        return prompt | structured_llm


class PydanticChainStrategy:
    """Uses PydanticOutputParser via prompt | llm | parser."""

    def build(
        self,
        prompt: ChatPromptTemplate,
        llm: Any,
        schema: Optional[Type[BaseModel]] = None,
    ) -> RunnableSequence:
        if schema is None:
            raise ValueError("PydanticChainStrategy requires a Pydantic schema class.")
        parser = PydanticOutputParser(pydantic_object=schema)
        return prompt | llm | parser


class JsonChainStrategy:
    """Uses JsonOutputParser for raw JSON array or dict parsing."""

    def build(
        self,
        prompt: ChatPromptTemplate,
        llm: Any,
        schema: Optional[Type[BaseModel]] = None,
    ) -> RunnableSequence:
        parser = JsonOutputParser(pydantic_object=schema) if schema else JsonOutputParser()
        return prompt | llm | parser


class RawChainStrategy:
    """Uses StrOutputParser to return string content directly."""

    def build(
        self,
        prompt: ChatPromptTemplate,
        llm: Any,
        schema: Optional[Type[BaseModel]] = None,
    ) -> RunnableSequence:
        return prompt | llm | StrOutputParser()


class ChainStrategyRegistry:
    """Registry maintaining available chain strategies (Open for extension via register())."""

    def __init__(self) -> None:
        self._strategies: Dict[str, ChainStrategy] = {
            "structured": StructuredChainStrategy(),
            "pydantic": PydanticChainStrategy(),
            "json": JsonChainStrategy(),
            "raw": RawChainStrategy(),
        }

    def register(self, name: str, strategy: ChainStrategy) -> None:
        """Register a new chain strategy without modifying core library code (OCP)."""
        self._strategies[name] = strategy

    def get(self, name_or_strategy: Union[str, ChainStrategy]) -> ChainStrategy:
        """Resolve a strategy by name or return the strategy instance directly (DIP)."""
        if isinstance(name_or_strategy, ChainStrategy):
            return name_or_strategy
        if isinstance(name_or_strategy, str):
            if name_or_strategy in self._strategies:
                return self._strategies[name_or_strategy]
            raise ValueError(
                f"Unknown chain mode '{name_or_strategy}'. "
                f"Available modes: {list(self._strategies.keys())}"
            )
        raise TypeError(f"Expected str or ChainStrategy, got {type(name_or_strategy)}")


_DEFAULT_REGISTRY = ChainStrategyRegistry()


def register_chain_strategy(name: str, strategy: ChainStrategy) -> None:
    """Global registration hook for custom chain strategies (OCP)."""
    _DEFAULT_REGISTRY.register(name, strategy)


def build_chain(
    prompt: ChatPromptTemplate,
    llm: Any,
    *,
    schema: Optional[Type[BaseModel]] = None,
    mode: Union[str, ChainStrategy] = "structured",
    registry: Optional[ChainStrategyRegistry] = None,
) -> RunnableSequence:
    """Build a LangChain LCEL RunnableSequence using the specified strategy (DIP)."""
    reg = registry or _DEFAULT_REGISTRY
    strategy = reg.get(mode)
    return strategy.build(prompt=prompt, llm=llm, schema=schema)
