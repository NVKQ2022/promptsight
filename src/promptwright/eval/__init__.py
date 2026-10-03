"""Evaluation and Golden Set regression testing framework (PromtEngineering.md §17)."""

from promptwright.eval.evaluators import (
    CustomFunctionEvaluator,
    Evaluator,
    FieldMatchEvaluator,
    SchemaComplianceEvaluator,
)
from promptwright.eval.models import (
    EvaluationResult,
    GoldenSet,
    GoldenSetReport,
    GoldenTestCase,
)
from promptwright.eval.runner import GoldenSetRunner

__all__ = [
    "GoldenTestCase",
    "GoldenSet",
    "EvaluationResult",
    "GoldenSetReport",
    "Evaluator",
    "SchemaComplianceEvaluator",
    "FieldMatchEvaluator",
    "CustomFunctionEvaluator",
    "GoldenSetRunner",
]
