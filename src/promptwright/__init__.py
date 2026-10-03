"""PromptWright — Production-grade prompt engineering built on LangChain."""

from promptwright.builder import PromptBuilder
from promptwright.chain import (
    ChainStrategy,
    ChainStrategyRegistry,
    JsonChainStrategy,
    PydanticChainStrategy,
    RawChainStrategy,
    StructuredChainStrategy,
    build_chain,
    register_chain_strategy,
)
from promptwright.middleware import (
    AntiPatternValidator,
    AutoDelimiterMiddleware,
    BaseMiddleware,
    ConstraintsStyleRule,
    IssueSeverity,
    Middleware,
    OutputFormatRule,
    PipelineComponent,
    PromptValidator,
    RoleAndGoalRule,
    SectionTransformer,
    StrictGroundingMiddleware,
    TaskClarityRule,
    ValidationIssue,
    ValidationRule,
    VerificationChecklistRule,
)
from promptwright.presets import (
    DefaultClassificationResult,
    create_classification_prompt,
    create_extraction_prompt,
)
from promptwright.few_shot import ExampleSelector, StaticExampleSelector
from promptwright.renderers import MarkdownSectionRenderer, PromptRenderer
from promptwright.sections import ContextBlock, Example, PromptSections

__version__ = "0.1.0"

__all__ = [
    # Core Builder & Sections
    "PromptBuilder",
    "PromptSections",
    "ContextBlock",
    "Example",
    "ExampleSelector",
    "StaticExampleSelector",
    # Renderers (SRP & DIP)
    "PromptRenderer",
    "MarkdownSectionRenderer",
    # Middleware & Segregated Protocols (ISP & LSP)
    "Middleware",
    "SectionTransformer",
    "PromptValidator",
    "PipelineComponent",
    "BaseMiddleware",
    "ValidationIssue",
    "IssueSeverity",
    # Validation Rules (SRP & OCP)
    "ValidationRule",
    "RoleAndGoalRule",
    "TaskClarityRule",
    "OutputFormatRule",
    "ConstraintsStyleRule",
    "VerificationChecklistRule",
    "AntiPatternValidator",
    "AutoDelimiterMiddleware",
    "StrictGroundingMiddleware",
    # Chain Strategies (OCP & DIP)
    "build_chain",
    "ChainStrategy",
    "ChainStrategyRegistry",
    "StructuredChainStrategy",
    "PydanticChainStrategy",
    "JsonChainStrategy",
    "RawChainStrategy",
    "register_chain_strategy",
    # Presets
    "create_extraction_prompt",
    "create_classification_prompt",
    "DefaultClassificationResult",
]
