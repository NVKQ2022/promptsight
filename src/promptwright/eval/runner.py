"""Test runner executing Golden Sets against LangChain runnables (PromtEngineering.md §17)."""

from __future__ import annotations

import time
from typing import Any, List, Optional

from promptwright.eval.evaluators import Evaluator, FieldMatchEvaluator, SchemaComplianceEvaluator
from promptwright.eval.models import EvaluationResult, GoldenSet, GoldenSetReport, GoldenTestCase


class GoldenSetRunner:
    """Automates prompt regression testing and performance benchmarking."""

    def __init__(
        self,
        chain: Any,
        golden_set: GoldenSet,
        evaluators: Optional[List[Evaluator]] = None,
    ) -> None:
        self.chain = chain
        self.golden_set = golden_set
        self.evaluators: List[Evaluator] = evaluators or [
            SchemaComplianceEvaluator(),
            FieldMatchEvaluator(),
        ]

    def run_case(self, case: GoldenTestCase) -> EvaluationResult:
        """Run a single test case through the chain and evaluate results."""
        start_time = time.perf_counter()
        actual_output: Any = None
        error_msg: Optional[str] = None
        passed = True
        scores: List[float] = []
        details: dict[str, Any] = {}

        try:
            actual_output = self.chain.invoke(case.input_variables)
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            passed = False
            scores.append(0.0)

        latency_ms = (time.perf_counter() - start_time) * 1000

        if actual_output is not None:
            for idx, ev in enumerate(self.evaluators):
                ev_pass, ev_score, ev_details = ev.evaluate(case, actual_output)
                scores.append(ev_score)
                details[f"evaluator_{idx}"] = ev_details
                if not ev_pass:
                    passed = False

        avg_score = sum(scores) / len(scores) if scores else (1.0 if passed else 0.0)

        return EvaluationResult(
            case_id=case.id,
            passed=passed,
            score=avg_score,
            latency_ms=latency_ms,
            actual_output=actual_output,
            error=error_msg,
            details=details,
        )

    def run(self) -> GoldenSetReport:
        """Execute all test cases in the golden set and generate a full report."""
        results: List[EvaluationResult] = []
        total_latency = 0.0
        passed_count = 0

        for case in self.golden_set.cases:
            res = self.run_case(case)
            results.append(res)
            total_latency += res.latency_ms
            if res.passed:
                passed_count += 1

        total = len(self.golden_set.cases)
        pass_rate = passed_count / total if total > 0 else 1.0
        avg_latency = total_latency / total if total > 0 else 0.0

        return GoldenSetReport(
            name=self.golden_set.name,
            total_cases=total,
            passed_cases=passed_count,
            failed_cases=total - passed_count,
            pass_rate=pass_rate,
            avg_latency_ms=avg_latency,
            results=results,
        )
