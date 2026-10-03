"""AI Prompt Generator using an LLM to engineer prompts adhering to PromtEngineering.md (§20)."""

from __future__ import annotations

import logging
from typing import Any, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from promptsight.meta.models import GeneratedPromptSpec
from promptsight.meta.prompts import META_PROMPT_SYSTEM, META_PROMPT_USER_TEMPLATE

logger = logging.getLogger(__name__)


class AIPromptGenerator:
    """Uses a LangChain LLM to design production-quality prompts from raw user tasks."""

    def __init__(self, llm: Any) -> None:
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=GeneratedPromptSpec)

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", META_PROMPT_SYSTEM + "\n\n{format_instructions}"),
                ("human", META_PROMPT_USER_TEMPLATE),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

    def generate(
        self,
        user_task: str,
        *,
        additional_context: Optional[str] = None,
    ) -> GeneratedPromptSpec:
        """Engineer a production-grade prompt from a task description.

        Args:
            user_task: Natural language description of what the user wants the prompt to do.
            additional_context: Optional domain context, rules, or schemas to embed.

        Returns:
            GeneratedPromptSpec with structured role, task, constraints, examples, and to_builder() conversion.
        """
        ctx_block = ""
        if additional_context:
            ctx_block = f"<additional_context>\n{additional_context}\n</additional_context>"

        # Strategy 1: Use native structured output if supported
        if hasattr(self.llm, "with_structured_output"):
            try:
                # Omit parser format_instructions when using structured output
                clean_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", META_PROMPT_SYSTEM),
                        ("human", META_PROMPT_USER_TEMPLATE),
                    ]
                )
                chain = clean_prompt | self.llm.with_structured_output(GeneratedPromptSpec)
                result = chain.invoke(
                    {"user_task": user_task, "additional_context_block": ctx_block}
                )
                if isinstance(result, GeneratedPromptSpec):
                    return result
            except (NotImplementedError, AttributeError, ValueError) as exc:
                logger.info(
                    "Native structured output not supported or failed (%s); falling back to PydanticOutputParser.",
                    exc,
                )
            except Exception as exc:
                logger.warning(
                    "Unexpected error during structured output (%s); attempting fallback parser.",
                    exc,
                )

        # Strategy 2: Prompt + PydanticOutputParser
        chain = self.prompt_template | self.llm | self.parser
        return chain.invoke({"user_task": user_task, "additional_context_block": ctx_block})


def generate_prompt_from_task(
    user_task: str,
    llm: Any,
    *,
    additional_context: Optional[str] = None,
) -> GeneratedPromptSpec:
    """Convenience function: use an LLM to engineer a prompt from a task description.

    Args:
        user_task: Natural language description of the prompt requirements.
        llm: Any LangChain chat model.
        additional_context: Optional background data or requirements.

    Returns:
        GeneratedPromptSpec with .to_builder() and .to_markdown() helpers.
    """
    generator = AIPromptGenerator(llm=llm)
    return generator.generate(user_task=user_task, additional_context=additional_context)
