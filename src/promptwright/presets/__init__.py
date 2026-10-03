"""Pre-engineered prompt presets for standard tasks."""

from promptwright.presets.classification import (
    DefaultClassificationResult,
    create_classification_prompt,
)
from promptwright.presets.extraction import create_extraction_prompt

__all__ = [
    "create_extraction_prompt",
    "create_classification_prompt",
    "DefaultClassificationResult",
]
