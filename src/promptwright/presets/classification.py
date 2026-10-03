"""Pre-engineered preset for Classification & Intent Routing (Use Case 2)."""

from __future__ import annotations

from typing import List, Optional, Type

from pydantic import BaseModel, Field

from promptwright.builder import PromptBuilder


class DefaultClassificationResult(BaseModel):
    """Standard classification result with reasoning and evidence."""

    category: str = Field(description="The chosen category from the allowed taxonomy")
    reasoning: str = Field(description="1-2 sentences justifying the classification")
    evidence_span: Optional[str] = Field(
        default=None,
        description="Exact quote or phrase from the input supporting the decision",
    )


def create_classification_prompt(
    categories: List[str],
    *,
    domain: str = "text",
    input_variable: str = "text",
    schema: Optional[Type[BaseModel]] = None,
    allow_unresolved: bool = True,
    fallback_category: str = "other",
) -> PromptBuilder:
    """Create a production-grade prompt for text classification / labeling.

    Args:
        categories: The list of allowed classification categories / labels.
        domain: Domain description (e.g., 'customer support ticket', 'product review', 'intent').
        input_variable: The LangChain template variable name for the target text.
        schema: Optional custom Pydantic schema (defaults to DefaultClassificationResult).
        allow_unresolved: If True, specifies fallback behavior when ambiguous or out of taxonomy.
        fallback_category: Category name to assign when out of scope.
    """
    categories_str = ", ".join(f"`{c}`" for c in categories)
    target_schema = schema or DefaultClassificationResult

    builder = (
        PromptBuilder()
        .role(f"Senior {domain.capitalize()} Classification Specialist")
        .goal(f"classify the provided {domain} into exactly one of the allowed categories")
        .inputs(**{input_variable: f"Input {domain} to classify"})
        .task(
            f"Step 1: Analyze the input delimited inside <{input_variable}>.",
            f"Step 2: Evaluate the intent and content against allowed categories: {categories_str}.",
            "Step 3: Select the single most accurate category.",
            "Step 4: Cite specific evidence from the text justifying the choice.",
        )
        .constraints(
            f"Allowed categories: {categories_str}.",
            "You MUST select only from the allowed category list verbatim.",
            "Do not invent new categories or modify the category names.",
        )
        .output_schema(target_schema)
        .verify(
            "Selected category is strictly from the allowed categories list",
            "Reasoning references concrete evidence in the input text",
            "Output strictly conforms to the requested schema",
        )
    )

    if allow_unresolved and fallback_category in categories:
        builder.constraints(
            f"If the text does not match any specific category, assign `{fallback_category}`."
        )

    return builder
