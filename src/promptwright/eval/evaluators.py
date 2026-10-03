"""Built-in evaluation strategies for Golden Set test cases."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Type, runtime_checkable

from pydantic import BaseModel

from promptwright.eval.models import GoldenTestCase


@runtime_checkable
class Evaluator(Protocol):
    """Protocol for evaluating prompt output against test criteria."""

    def evaluate(
        self, case: GoldenTestCase, actual_output: Any
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """Return (passed, score_0_to_1, details_dict)."""
        ...


class SchemaComplianceEvaluator(Evaluator):
    """Checks whether the actual output conforms to the required Pydantic schema."""

    def __init__(self, schema: Optional[Type[BaseModel]] = None):
        self.schema = schema

    def evaluate(
        self, case: GoldenTestCase, actual_output: Any
    ) -> Tuple[bool, float, Dict[str, Any]]:
        if actual_output is None:
            return False, 0.0, {"reason": "Output is None"}

        if self.schema is not None:
            if isinstance(actual_output, self.schema):
                return True, 1.0, {"type": "schema_instance_match"}
            if isinstance(actual_output, dict):
                try:
                    self.schema.model_validate(actual_output)
                    return True, 1.0, {"type": "dict_validated_successfully"}
                except Exception as e:
                    return False, 0.0, {"error": str(e)}

        # Fallback: check if non-empty
        if isinstance(actual_output, (dict, list)) and len(actual_output) > 0:
            return True, 1.0, {"type": "valid_non_empty_json"}

        return True, 1.0, {"type": "output_present"}


class FieldMatchEvaluator(Evaluator):
    """Evaluates whether fields in expected_output match actual_output."""

    def __init__(self, key_fields: Optional[List[str]] = None, case_sensitive: bool = False):
        self.key_fields = key_fields
        self.case_sensitive = case_sensitive

    def evaluate(
        self, case: GoldenTestCase, actual_output: Any
    ) -> Tuple[bool, float, Dict[str, Any]]:
        if not case.expected_output:
            return True, 1.0, {"note": "No expected_output defined"}

        expected = case.expected_output
        actual = actual_output

        # Convert Pydantic models to dicts if needed
        if isinstance(expected, BaseModel):
            expected = expected.model_dump()
        if isinstance(actual, BaseModel):
            actual = actual.model_dump()

        if not isinstance(expected, dict) or not isinstance(actual, dict):
            # Direct scalar comparison
            passed = str(expected).strip() == str(actual).strip()
            return passed, 1.0 if passed else 0.0, {"expected": expected, "actual": actual}

        # Dict field comparison
        target_keys = self.key_fields or list(expected.keys())
        matches = 0
        mismatches: Dict[str, Any] = {}

        for k in target_keys:
            if k not in expected:
                continue
            exp_v = expected[k]
            act_v = actual.get(k)

            is_match = False
            if not self.case_sensitive and isinstance(exp_v, str) and isinstance(act_v, str):
                is_match = exp_v.strip().lower() == act_v.strip().lower()
            else:
                is_match = exp_v == act_v

            if is_match:
                matches += 1
            else:
                mismatches[k] = {"expected": exp_v, "actual": act_v}

        score = matches / len(target_keys) if target_keys else 1.0
        passed = score == 1.0
        return (
            passed,
            score,
            {"matches": matches, "total": len(target_keys), "mismatches": mismatches},
        )


class CustomFunctionEvaluator(Evaluator):
    """Adapter wrapping a custom callable (case, actual) -> (passed, score, details)."""

    def __init__(self, fn: Callable[[GoldenTestCase, Any], Tuple[bool, float, Dict[str, Any]]]):
        self.fn = fn

    def evaluate(
        self, case: GoldenTestCase, actual_output: Any
    ) -> Tuple[bool, float, Dict[str, Any]]:
        return self.fn(case, actual_output)
