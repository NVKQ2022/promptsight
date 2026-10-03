"""Pre-engineered preset for Structured Data Extraction (Use Case 1)."""

from __future__ import annotations

from typing import Optional, Type
from pydantic import BaseModel

from promptwright.builder import PromptBuilder
from promptwright.middleware.grounding import StrictGroundingMiddleware


def create_extraction_prompt(
    schema: Type[BaseModel],
    *,
    domain: str = "document",
    input_variable: str = "document",
    role: Optional[str] = None,
    allow_missing: bool = True,
) -> PromptBuilder:
    """Create a production-grade prompt for structured data extraction.

    Enforces strict grounding, schema compliance, and safe missing-field behavior.

    Args:
        schema: The Pydantic model defining the expected output structure.
        domain: Context domain (e.g., 'invoice', 'resume', 'medical report', 'customer query').
        input_variable: The LangChain template variable name for the source text.
        role: Optional role override.
        allow_missing: If True, instructs model to set missing fields to null rather than guessing.
    """
    builder = (
        PromptBuilder()
        .role(role or f"Senior {domain.capitalize()} Information Extraction Specialist")
        .goal(f"extract accurate structured information from the provided {domain} strictly matching the required schema")
        .inputs(**{input_variable: f"Raw {domain} text to extract data from"})
        .task(
            f"Step 1: Read the delimited <{input_variable}> thoroughly.",
            f"Step 2: Identify and extract all entities and fields matching the output schema.",
            f"Step 3: Normalize data types (dates, numbers, strings) per schema specifications.",
            f"Step 4: Verify all extracted values are explicitly supported by the text.",
        )
        .constraints(
            f"Extract only information directly present in the <{input_variable}>.",
            "Do not extrapolate, assume, or fabricate any facts not in the source text.",
        )
        .output_schema(schema)
        .verify(
            f"Every extracted field is directly grounded in the source <{input_variable}>",
            "Data types match the output schema exactly",
            "No ungrounded or speculative values are included",
        )
        .use(StrictGroundingMiddleware(allow_guessing=not allow_missing))
    )

    if allow_missing:
        builder.constraints(
            "If an optional field is missing from the source text, set it to null. Never guess or hallucinate."
        )

    return builder
