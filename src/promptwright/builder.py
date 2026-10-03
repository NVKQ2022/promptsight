"""Core PromptBuilder with fluent API and middleware support."""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Type, Union
from pydantic import BaseModel

try:
    from langchain_core.prompts import (
        ChatPromptTemplate,
        FewShotChatMessagePromptTemplate,
        PromptTemplate,
    )
    from langchain_core.runnables import RunnableSequence
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "langchain-core is required. Install with: pip install langchain-core"
    ) from e

from promptwright.chain import build_chain
from promptwright.few_shot import format_example_payload
from promptwright.middleware.base import (
    IssueSeverity,
    Middleware,
    MiddlewareType,
    ValidationIssue,
    wrap_middleware,
)
from promptwright.middleware.validator import AntiPatternValidator
from promptwright.sections import ContextBlock, Example, PromptSections


class PromptBuilder:
    """Fluent builder for constructing production-grade LangChain prompts.

    Adheres to PromtEngineering.md principles and supports middleware plugins.
    """

    def __init__(self, sections: Optional[PromptSections] = None) -> None:
        self.sections: PromptSections = sections or PromptSections()
        self._middlewares: List[Middleware] = [AntiPatternValidator(strict=False)]
        self._user_template: Optional[str] = None

    def role(self, role: str) -> "PromptBuilder":
        """Set the role of the model (PromtEngineering.md §4.1)."""
        self.sections.role = role
        return self

    def goal(self, goal: str) -> "PromptBuilder":
        """Set the desired outcome / goal."""
        self.sections.goal = goal
        return self

    def context(
        self,
        content: str,
        tag: str = "context",
        name: str = "",
        treat_as_data: bool = True,
    ) -> "PromptBuilder":
        """Add an authoritative context block wrapped in delimiters (§5, §10)."""
        self.sections.context_blocks.append(
            ContextBlock(name=name or tag, content=content, tag=tag, treat_as_data=treat_as_data)
        )
        return self

    def inputs(self, *names: str, **named_inputs: str) -> "PromptBuilder":
        """Register runtime variables and optional descriptions (§6)."""
        for n in names:
            self.sections.inputs[n] = "Runtime input"
        for k, v in named_inputs.items():
            self.sections.inputs[k] = v
        return self

    def task(self, *steps: str) -> "PromptBuilder":
        """Define the primary task or decomposed steps (§7, §12)."""
        self.sections.tasks.extend(steps)
        return self

    def constraints(self, *rules: str) -> "PromptBuilder":
        """Add explicit constraints and limits (§8)."""
        self.sections.constraints.extend(rules)
        return self

    def output_schema(self, schema: Type[BaseModel]) -> "PromptBuilder":
        """Set deterministic output shape via a Pydantic model (§11)."""
        self.sections.output_schema = schema
        return self

    def output_format(self, text: str) -> "PromptBuilder":
        """Set custom output format description (§11)."""
        self.sections.output_format_text = text
        return self

    def example(
        self,
        input_data: Any,
        output_data: Any,
        description: Optional[str] = None,
    ) -> "PromptBuilder":
        """Add a few-shot example (§9)."""
        self.sections.examples.append(
            Example(
                input_text=format_example_payload(input_data),
                output_text=format_example_payload(output_data),
                description=description,
            )
        )
        return self

    def verify(self, *checklist_items: str) -> "PromptBuilder":
        """Add verification self-check checklist items (§13)."""
        self.sections.verifications.extend(checklist_items)
        return self

    def user_template(self, template: str) -> "PromptBuilder":
        """Set custom human message template. Defaults to delimited input variables."""
        self._user_template = template
        return self

    def use(self, middleware: MiddlewareType) -> "PromptBuilder":
        """Register a middleware plugin (transform, validate, or enrich)."""
        self._middlewares.append(wrap_middleware(middleware))
        return self

    def validate(self, strict: bool = False) -> List[ValidationIssue]:
        """Run all registered validation middlewares against current sections."""
        issues: List[ValidationIssue] = []
        for mw in self._middlewares:
            issues.extend(mw.validate(self.sections))

        if strict:
            errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
            if errors:
                error_msgs = "\n".join(f"- {str(e)}" for e in errors)
                raise ValueError(f"Prompt validation failed with {len(errors)} error(s):\n{error_msgs}")

        return issues

    def _apply_transforms(self) -> PromptSections:
        """Apply all middleware transformations to a copy of sections."""
        working_sections = copy.deepcopy(self.sections)
        for mw in self._middlewares:
            working_sections = mw.transform(working_sections)
        return working_sections

    def _render_user_message(self, sections: PromptSections) -> str:
        """Render the human input message."""
        if self._user_template:
            return self._user_template

        if not sections.inputs:
            return "{input}"

        blocks: List[str] = []
        for var_name in sections.inputs:
            blocks.append(f"<{var_name}>\n{{{var_name}}}\n</{var_name}>")

        return "\n\n".join(blocks)

    def build(
        self,
        *,
        strict: bool = False,
        with_few_shot: bool = True,
        template_format: str = "f-string",
    ) -> ChatPromptTemplate:
        """Compile the prompt into a LangChain ChatPromptTemplate.

        Args:
            strict: If True, raises ValueError if any validation error occurs.
            with_few_shot: If True, appends FewShotChatMessagePromptTemplate if examples exist.
            template_format: "f-string" (recommended per security guide).

        Returns:
            LangChain ChatPromptTemplate ready for LCEL.
        """
        # 1. Validate
        self.validate(strict=strict)

        # 2. Transform sections via registered middlewares
        sections = self._apply_transforms()

        # 3. Render system message
        system_content = sections.render_system_prompt(escape_braces_for_fstring=True)

        messages: List[Any] = [("system", system_content)]

        # 4. Handle Few-Shot examples
        if with_few_shot and sections.examples:
            example_prompt = ChatPromptTemplate.from_messages(
                [("human", "{input}"), ("ai", "{output}")]
            )
            examples_payload = [
                {"input": ex.input_text, "output": ex.output_text}
                for ex in sections.examples
            ]
            few_shot = FewShotChatMessagePromptTemplate(
                examples=examples_payload,
                example_prompt=example_prompt,
            )
            messages.append(few_shot)

        # 5. Render human message
        human_content = self._render_user_message(sections)
        messages.append(("human", human_content))

        return ChatPromptTemplate.from_messages(messages, template_format=template_format)

    def to_chain(
        self,
        llm: Any,
        *,
        mode: Literal["structured", "pydantic", "json", "raw"] = "structured",
        strict: bool = False,
        with_few_shot: bool = True,
    ) -> RunnableSequence:
        """Convenience method: compile prompt and bind directly to an LLM chain.

        Args:
            llm: LangChain Chat Model.
            mode: 'structured' | 'pydantic' | 'json' | 'raw'.
            strict: Enforce strict validation.
            with_few_shot: Include few-shot examples.
        """
        prompt = self.build(strict=strict, with_few_shot=with_few_shot)
        return build_chain(
            prompt=prompt,
            llm=llm,
            schema=self.sections.output_schema,
            mode=mode,
        )
