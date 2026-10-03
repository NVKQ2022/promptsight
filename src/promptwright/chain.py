"""LangChain LCEL chain builder bridging prompts and LLMs."""

from __future__ import annotations

from typing import Any, Literal, Optional, Type
from pydantic import BaseModel

try:
    from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser, StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableSequence
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "langchain-core is required to build chains. Install with: pip install langchain-core"
    ) from e


def build_chain(
    prompt: ChatPromptTemplate,
    llm: Any,
    *,
    schema: Optional[Type[BaseModel]] = None,
    mode: Literal["structured", "pydantic", "json", "raw"] = "structured",
) -> RunnableSequence:
    """Build a standard LangChain LCEL RunnableSequence.

    Modes:
    - 'structured' (default): Uses `llm.with_structured_output(schema)`.
      Best for tool-calling/function-calling models (OpenAI, Anthropic, Gemini).
    - 'pydantic': Uses `PydanticOutputParser` via `prompt | llm | parser`.
    - 'json': Uses `JsonOutputParser` for JSON dict/array output.
    - 'raw': Uses `StrOutputParser` returning raw text.
    """
    if mode == "structured":
        if schema is None:
            raise ValueError("mode='structured' requires a Pydantic schema class.")
        if not hasattr(llm, "with_structured_output"):
            raise ValueError(
                f"LLM {type(llm)} does not implement with_structured_output(). "
                "Use mode='pydantic' or mode='json' instead."
            )
        structured_llm = llm.with_structured_output(schema)
        return prompt | structured_llm

    if mode == "pydantic":
        if schema is None:
            raise ValueError("mode='pydantic' requires a Pydantic schema class.")
        parser = PydanticOutputParser(pydantic_object=schema)
        return prompt | llm | parser

    if mode == "json":
        json_parser = JsonOutputParser(pydantic_object=schema) if schema else JsonOutputParser()
        return prompt | llm | json_parser

    if mode == "raw":
        return prompt | llm | StrOutputParser()

    raise ValueError(f"Unknown mode '{mode}'. Choose from 'structured', 'pydantic', 'json', 'raw'.")
