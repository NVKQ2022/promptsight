"""Data models for Golden Set evaluation and regression reporting (PromtEngineering.md §17)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel


@dataclass
class GoldenTestCase:
    """A single representative test case for prompt evaluation."""
    id: str
    input_variables: Dict[str, Any]
    expected_output: Optional[Any] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    criteria: List[str] = field(default_factory=list)


@dataclass
class GoldenSet:
    """Collection of versioned golden test cases."""
    name: str = "default_golden_set"
    cases: List[GoldenTestCase] = field(default_factory=list)

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]], name: str = "golden_set") -> "GoldenSet":
        cases: List[GoldenTestCase] = []
        for idx, item in enumerate(data, start=1):
            case_id = item.get("id") or f"case_{idx:03d}"
            # Support inputs inside "input" or "input_variables" or "inputs"
            input_vars = (
                item.get("input_variables")
                or item.get("inputs")
                or item.get("input")
                or {}
            )
            if not isinstance(input_vars, dict):
                input_vars = {"input": input_vars}

            expected = item.get("expected_output") or item.get("expected")
            desc = item.get("description") or item.get("_comment")
            tags = item.get("tags") or []
            criteria = item.get("criteria") or []

            cases.append(
                GoldenTestCase(
                    id=str(case_id),
                    input_variables=input_vars,
                    expected_output=expected,
                    description=desc,
                    tags=tags,
                    criteria=criteria,
                )
            )
        return cls(name=name, cases=cases)

    @classmethod
    def from_file(cls, path_or_str: Union[str, Path]) -> "GoldenSet":
        path = Path(path_or_str)
        content = path.read_text(encoding="utf-8")
        if path.suffix in (".yaml", ".yml"):
            import yaml  # type: ignore[import-untyped]
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)

        if isinstance(data, list):
            return cls.from_list(data, name=path.stem)
        if isinstance(data, dict) and "cases" in data:
            return cls.from_list(data["cases"], name=data.get("name", path.stem))
        raise ValueError(f"Invalid golden set format in {path}")


@dataclass
class EvaluationResult:
    """Result of running a single GoldenTestCase against a chain."""
    case_id: str
    passed: bool
    score: float  # 0.0 to 1.0
    latency_ms: float
    actual_output: Any
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GoldenSetReport:
    """Aggregated evaluation and regression report."""
    name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    avg_latency_ms: float
    results: List[EvaluationResult] = field(default_factory=list)

    def summary(self) -> str:
        """Render a clean Markdown evaluation summary table."""
        pct = f"{self.pass_rate * 100:.1f}%"
        status_icon = "✅" if self.passed_cases == self.total_cases else "⚠️"

        lines = [
            f"## {status_icon} Golden Set Evaluation Report: `{self.name}`",
            "",
            f"- **Pass Rate**: {pct} ({self.passed_cases}/{self.total_cases} passed)",
            f"- **Average Latency**: {self.avg_latency_ms:.1f} ms",
            "",
            "| Case ID | Status | Score | Latency | Error / Notes |",
            "|---|---|---|---|---|",
        ]

        for r in self.results:
            st = "PASS" if r.passed else "FAIL"
            err = r.error or "-"
            if len(err) > 50:
                err = err[:47] + "..."
            lines.append(f"| `{r.case_id}` | {st} | {r.score:.2f} | {r.latency_ms:.0f} ms | {err} |")

        return "\n".join(lines)
