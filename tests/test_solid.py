"""Tests explicitly validating adherence to SOLID design principles."""

import pytest
from typing import List, Optional, Type
from pydantic import BaseModel
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence

from promptwright import (
    PromptBuilder,
    PromptRenderer,
    PromptSections,
    PromptValidator,
    SectionTransformer,
    ValidationIssue,
    ValidationRule,
    AntiPatternValidator,
    ChainStrategy,
    register_chain_strategy,
)


# ============================================================================
# 1. Single Responsibility & Dependency Inversion: Custom PromptRenderer
# ============================================================================
class XMLPromptRenderer(PromptRenderer):
    """Custom renderer formatting instructions in pure XML format (DIP & OCP)."""

    def render_system(self, sections: PromptSections) -> str:
        return f"<system><role>{sections.role}</role><task>{sections.tasks[0]}</task></system>"

    def render_user(self, sections: PromptSections, custom_template: Optional[str] = None) -> str:
        return f"<user>{custom_template or '{input}'}</user>"


def test_custom_renderer_dependency_inversion():
    builder = (
        PromptBuilder()
        .role("Data Processor")
        .task("Extract entities")
        .with_renderer(XMLPromptRenderer())
    )
    prompt = builder.build()
    messages = prompt.format_messages(input="test data")
    assert messages[0].content == "<system><role>Data Processor</role><task>Extract entities</task></system>"
    assert messages[1].content == "<user>test data</user>"


# ============================================================================
# 2. Open/Closed Principle: Custom Validation Rule
# ============================================================================
class MaxConstraintsRule(ValidationRule):
    """Enforce a maximum number of constraints to keep prompts compact (OCP)."""

    def __init__(self, max_constraints: int = 3):
        self.max_constraints = max_constraints

    def evaluate(self, sections: PromptSections) -> List[ValidationIssue]:
        if len(sections.constraints) > self.max_constraints:
            return [
                ValidationIssue(
                    code="TOO_MANY_CONSTRAINTS",
                    section="constraints",
                    message=f"Prompt has {len(sections.constraints)} constraints, exceeding max of {self.max_constraints}.",
                )
            ]
        return []


def test_custom_validation_rule_open_closed():
    custom_validator = AntiPatternValidator(rules=[MaxConstraintsRule(max_constraints=2)])

    builder = (
        PromptBuilder()
        .role("Reviewer")
        .task("Review PR")
        .output_format("text")
        .constraints("Rule 1", "Rule 2", "Rule 3")  # 3 constraints > max 2
        .use(custom_validator)
    )

    issues = builder.validate()
    constraint_issues = [i for i in issues if i.code == "TOO_MANY_CONSTRAINTS"]
    assert len(constraint_issues) == 1
    assert "exceeding max of 2" in constraint_issues[0].message


# ============================================================================
# 3. Interface Segregation Principle: Pure Transformer and Pure Validator
# ============================================================================
class PureTransformer(SectionTransformer):
    """Only transforms sections, does NOT implement validate()."""

    def transform(self, sections: PromptSections) -> PromptSections:
        sections.metadata["transformed_by_pure"] = True
        return sections


class PureValidator(PromptValidator):
    """Only validates sections, does NOT implement transform()."""

    def validate(self, sections: PromptSections) -> List[ValidationIssue]:
        return [
            ValidationIssue(
                code="PURE_VALIDATOR_CALLED",
                section="meta",
                message="Pure validator executed successfully.",
            )
        ]


def test_interface_segregation_principle():
    builder = (
        PromptBuilder()
        .role("Analyzer")
        .task("Analyze telemetry")
        .output_format("JSON")
        .use(PureTransformer())
        .use(PureValidator())
    )

    # Both run properly despite neither implementing the other's method
    issues = builder.validate()
    assert any(i.code == "PURE_VALIDATOR_CALLED" for i in issues)

    builder.build()
    transformed = builder._apply_transforms()
    assert transformed.metadata.get("transformed_by_pure") is True


# ============================================================================
# 4. Open/Closed Principle: Custom ChainStrategy
# ============================================================================
class UpperCaseRawChainStrategy(ChainStrategy):
    """Custom chain strategy that converts output to uppercase."""

    def build(
        self,
        prompt: ChatPromptTemplate,
        llm: FakeListChatModel,
        schema: Optional[Type[BaseModel]] = None,
    ) -> RunnableSequence:
        return prompt | llm | RunnableLambda(lambda msg: msg.content.upper())


def test_custom_chain_strategy_open_closed():
    # Register custom strategy
    register_chain_strategy("uppercase", UpperCaseRawChainStrategy())

    builder = (
        PromptBuilder()
        .role("Echo")
        .task("Echo back")
        .inputs(msg="Message")
    )
    fake_llm = FakeListChatModel(responses=["hello world"])

    # Test resolution by name
    chain = builder.to_chain(fake_llm, mode="uppercase")
    result = chain.invoke({"msg": "hello"})
    assert result == "HELLO WORLD"

    # Test direct strategy instance injection (DIP)
    chain_direct = builder.to_chain(fake_llm, mode=UpperCaseRawChainStrategy())
    result_direct = chain_direct.invoke({"msg": "hello"})
    assert result_direct == "HELLO WORLD"
