"""PromptSight — Production-grade prompt engineering built on LangChain."""

from promptsight.builder import PromptBuilder
from promptsight.chain import (
    ChainStrategy,
    ChainStrategyRegistry,
    JsonChainStrategy,
    PydanticChainStrategy,
    RawChainStrategy,
    StructuredChainStrategy,
    build_chain,
    register_chain_strategy,
)
from promptsight.eval import (
    GoldenSet,
    GoldenSetReport,
    GoldenSetRunner,
    GoldenTestCase,
)
from promptsight.few_shot import ExampleSelector, StaticExampleSelector
from promptsight.meta import (
    AIPromptGenerator,
    GeneratedPromptSpec,
    generate_prompt_from_task,
)
from promptsight.middleware import (
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
from promptsight.presets import (
    DefaultClassificationResult,
    create_classification_prompt,
    create_extraction_prompt,
)
from promptsight.renderers import MarkdownSectionRenderer, PromptRenderer
from promptsight.sections import ContextBlock, Example, PromptSections

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
    # Evaluation (Challenge 4)
    "GoldenSetRunner",
    "GoldenSet",
    "GoldenTestCase",
    "GoldenSetReport",
    # Meta-Prompting & AI Prompt Generation (§20)
    "AIPromptGenerator",
    "generate_prompt_from_task",
    "GeneratedPromptSpec",
]
