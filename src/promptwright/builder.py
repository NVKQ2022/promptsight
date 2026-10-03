"""Core PromptBuilder orchestrating construction, middleware, and rendering (SOLID compliant)."""

from __future__ import annotations

import copy
from typing import Any, List, Literal, Optional, Type, Union

from pydantic import BaseModel

try:
    from langchain_core.prompts import (
        ChatPromptTemplate,
        FewShotChatMessagePromptTemplate,
    )
    from langchain_core.runnables import RunnableSequence
except ImportError as e:  # pragma: no cover
    raise ImportError("langchain-core is required. Install with: pip install langchain-core") from e

from promptwright.chain import ChainStrategy, build_chain
from promptwright.few_shot import format_example_payload
from promptwright.middleware.base import (
    IssueSeverity,
    PipelineComponent,
    PromptValidator,
    SectionTransformer,
    ValidationIssue,
    is_transformer,
    is_validator,
)
from promptwright.middleware.validator import AntiPatternValidator
from promptwright.renderers.base import PromptRenderer
from promptwright.renderers.markdown import MarkdownSectionRenderer
from promptwright.sections import ContextBlock, Example, PromptSections


class PromptBuilder:
    """Fluent builder for constructing production-grade LangChain prompts.

    Adheres to SOLID principles:
    - Single Responsibility: Orchestrates prompt construction and configuration.
    - Open/Closed: Extensible via middlewares, validation rules, renderers, and chain strategies.
    - Liskov Substitution: Works with any compliant renderer or pipeline component.
    - Interface Segregation: Distinguishes transformers from validators.
    - Dependency Inversion: Depends on PromptRenderer and ChainStrategy abstractions.
    """

    def __init__(
        self,
        sections: Optional[PromptSections] = None,
        renderer: Optional[PromptRenderer] = None,
    ) -> None:
        self.sections: PromptSections = sections or PromptSections()
        self.renderer: PromptRenderer = renderer or MarkdownSectionRenderer()
        self._transformers: List[SectionTransformer] = []
        self._validators: List[PromptValidator] = [AntiPatternValidator(strict=False)]
        self._user_template: Optional[str] = None
        self._custom_example_prompt: Optional[ChatPromptTemplate] = None

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

    def output_schema(
        self,
        schema: Type[BaseModel],
        mode: Literal["full", "concise", "tools_only"] = "full",
    ) -> "PromptBuilder":
        """Set deterministic output shape via a Pydantic model (§11).

        Args:
            schema: Pydantic BaseModel defining fields and types.
            mode:
                - 'full': Injects complete JSON Schema into prompt text (default).
                - 'concise': Injects a compact summary of field names and types (saves tokens).
                - 'tools_only': Omits schema text from prompt body, relying on LLM tool definition (zero token duplication).
        """
        self.sections.output_schema = schema
        self.sections.schema_mode = mode
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

    def example_selector(
        self,
        selector: Any,
        example_prompt: Optional[ChatPromptTemplate] = None,
    ) -> "PromptBuilder":
        """Attach a dynamic example selector (e.g. LangChain BaseExampleSelector).

        Enables retrieval-augmented dynamic few-shots based on semantic similarity.
        """
        self.sections.example_selector = selector
        if example_prompt is not None:
            self._custom_example_prompt = example_prompt
        return self

    def verify(self, *checklist_items: str) -> "PromptBuilder":
        """Add verification self-check checklist items (§13)."""
        self.sections.verifications.extend(checklist_items)
        return self

    def user_template(self, template: str) -> "PromptBuilder":
        """Set custom human message template."""
        self._user_template = template
        return self

    def with_renderer(self, renderer: PromptRenderer) -> "PromptBuilder":
        """Inject a custom PromptRenderer implementation (DIP & OCP)."""
        self.renderer = renderer
        return self

    def use_transformer(self, transformer: PipelineComponent) -> "PromptBuilder":
        """Register an explicit transformer component or callable (PromptSections -> PromptSections)."""
        if is_transformer(transformer):
            self._transformers.append(transformer)  # type: ignore[arg-type]
        elif callable(transformer):

            class _FunctionTransformer:
                def transform(self, s: PromptSections) -> PromptSections:
                    res = transformer(s)
                    return res if isinstance(res, PromptSections) else s

            self._transformers.append(_FunctionTransformer())
        else:
            raise TypeError(
                f"Component {type(transformer)} must implement transform or be callable."
            )
        return self

    def use_validator(self, validator: PipelineComponent) -> "PromptBuilder":
        """Register an explicit validator component or callable (PromptSections -> List[ValidationIssue])."""
        if is_validator(validator):
            self._validators.append(validator)  # type: ignore[arg-type]
        elif callable(validator):

            class _FunctionValidator:
                def validate(self, s: PromptSections) -> List[ValidationIssue]:
                    res = validator(s)
                    return res if isinstance(res, list) else []

            self._validators.append(_FunctionValidator())
        else:
            raise TypeError(f"Component {type(validator)} must implement validate or be callable.")
        return self

    def use(self, component: PipelineComponent) -> "PromptBuilder":
        """Register a transformer, validator, or composite middleware component (ISP)."""
        added = False
        if is_transformer(component):
            self._transformers.append(component)  # type: ignore[arg-type]
            added = True
        if is_validator(component):
            self._validators.append(component)  # type: ignore[arg-type]
            added = True

        if not added and callable(component):
            # Check return type annotation if available without executing user code at registration
            try:
                import inspect

                sig = inspect.signature(component)
                ret = sig.return_annotation
                ret_str = str(ret).lower() if ret is not inspect.Signature.empty else ""
                if "list" in ret_str or "validationissue" in ret_str:
                    return self.use_validator(component)
            except (ValueError, TypeError):
                pass
            return self.use_transformer(component)

        if not added:
            raise TypeError(
                f"Component {type(component)} must implement transform, validate, or be callable."
            )

        return self

    def validate(self, strict: bool = False) -> List[ValidationIssue]:
        """Run all registered validation middlewares against current sections."""
        issues: List[ValidationIssue] = []
        for val in self._validators:
            issues.extend(val.validate(self.sections))

        if strict:
            errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
            if errors:
                error_msgs = "\n".join(f"- {str(e)}" for e in errors)
                raise ValueError(
                    f"Prompt validation failed with {len(errors)} error(s):\n{error_msgs}"
                )

        return issues

    def _apply_transforms(self) -> PromptSections:
        """Apply all transformer middlewares to a copy of sections."""
        working_sections = copy.deepcopy(self.sections)
        for tf in self._transformers:
            working_sections = tf.transform(working_sections)
        return working_sections

    def render_system(self) -> str:
        """Render the system prompt string directly without compiling to ChatPromptTemplate."""
        sections = self._apply_transforms()
        return self.renderer.render_system(sections)

    def render_user(self, custom_template: Optional[str] = None) -> str:
        """Render the user prompt string directly without compiling to ChatPromptTemplate."""
        sections = self._apply_transforms()
        return self.renderer.render_user(sections, custom_template or self._user_template)

    def build(
        self,
        *,
        strict: bool = False,
        with_few_shot: bool = True,
        template_format: str = "f-string",
    ) -> ChatPromptTemplate:
        """Compile the prompt into a LangChain ChatPromptTemplate."""
        # 1. Validate
        self.validate(strict=strict)

        # 2. Transform sections via registered transformers
        sections = self._apply_transforms()

        # 3. Delegate rendering to injected PromptRenderer (SRP & DIP)
        system_content = self.renderer.render_system(sections)
        messages: List[Any] = [("system", system_content)]

        # 4. Handle Few-Shot examples (Static or Dynamic)
        if with_few_shot:
            default_example_prompt = ChatPromptTemplate.from_messages(
                [("human", "{input}"), ("ai", "{output}")]
            )
            ex_prompt = self._custom_example_prompt or default_example_prompt

            if sections.example_selector is not None:
                from promptwright.few_shot import ensure_base_example_selector

                few_shot = FewShotChatMessagePromptTemplate(
                    example_selector=ensure_base_example_selector(sections.example_selector),
                    example_prompt=ex_prompt,
                )
                messages.append(few_shot)
            elif sections.examples:
                examples_payload = [
                    {"input": ex.input_text, "output": ex.output_text} for ex in sections.examples
                ]
                few_shot = FewShotChatMessagePromptTemplate(
                    examples=examples_payload,
                    example_prompt=ex_prompt,
                )
                messages.append(few_shot)

        # 5. Delegate user message rendering to injected PromptRenderer
        human_content = self.renderer.render_user(sections, self._user_template)
        messages.append(("human", human_content))

        return ChatPromptTemplate.from_messages(messages, template_format=template_format)

    def to_chain(
        self,
        llm: Any,
        *,
        mode: Union[str, ChainStrategy] = "structured",
        strict: bool = False,
        with_few_shot: bool = True,
    ) -> RunnableSequence:
        """Compile prompt and bind directly to an LLM chain via ChainStrategy (DIP)."""
        prompt = self.build(strict=strict, with_few_shot=with_few_shot)
        return build_chain(
            prompt=prompt,
            llm=llm,
            schema=self.sections.output_schema,
            mode=mode,
        )
