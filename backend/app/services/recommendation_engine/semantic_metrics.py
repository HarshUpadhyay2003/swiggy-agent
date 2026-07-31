"""
Stage 4F.1 Phase 5 — Semantic Metrics Calculator Module.
Single Source of Truth for all leakage, quality, distribution, and boundary metrics.
"""

import math
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel


class MetricReport(BaseModel):
    total_evaluated: int
    total_accepted: int
    total_rejected: int
    total_borderline: int
    domain_leakage_count: int
    context_leakage_count: int
    domain_leakage_pct: float
    context_leakage_pct: float
    semantic_precision_pct: float
    semantic_recall_pct: float
    recommendation_quality_score: float
    similarity_mean: float
    similarity_stddev: float
    suitability_mean: float
    suitability_stddev: float


class SemanticMetricsCalculator:
    """Single Source of Truth metric calculator ensuring 100% equality across Telemetry, Markdown, and JSON."""

    def calculate_domain_leakage(self, evaluations: List[Dict[str, Any]]) -> Tuple[int, float]:
        total = len(evaluations)
        leak_count = sum(1 for e in evaluations if e.get("is_forbidden") or "forbidden" in str(e.get("violations", "")).lower())
        pct = (leak_count / total * 100.0) if total > 0 else 0.0
        return leak_count, round(pct, 2)

    def calculate_context_leakage(self, evaluations: List[Dict[str, Any]]) -> Tuple[int, float]:
        total = len(evaluations)
        leak_count = sum(1 for e in evaluations if e.get("context_leakage") or "context" in str(e.get("violations", "")).lower())
        pct = (leak_count / total * 100.0) if total > 0 else 0.0
        return leak_count, round(pct, 2)


    def calculate_semantic_precision(self, evaluations: List[Dict[str, Any]]) -> float:
        accepted = [e for e in evaluations if e.get("decision") == "ACCEPT"]
        if not accepted:
            return 100.0
        correct = sum(1 for e in accepted if e.get("semantic_similarity", 1.0) >= 0.70 and not e.get("is_forbidden"))
        return round((correct / len(accepted)) * 100.0, 2)

    def calculate_semantic_recall(self, evaluations: List[Dict[str, Any]]) -> float:
        valid_candidates = [e for e in evaluations if not e.get("is_forbidden") and e.get("semantic_similarity", 1.0) >= 0.70]
        if not valid_candidates:
            return 100.0
        accepted_valid = sum(1 for e in valid_candidates if e.get("decision") == "ACCEPT")
        return round((accepted_valid / len(valid_candidates)) * 100.0, 2)

    def calculate_recommendation_quality(self, precision_pct: float, domain_leak_pct: float, context_leak_pct: float) -> float:
        rqs = precision_pct - (domain_leak_pct * 1.5) - (context_leak_pct * 1.0)
        return round(min(max(rqs, 0.0), 100.0), 2)

    def calculate_score_distribution(self, scores: List[float]) -> Dict[str, float]:
        if not scores:
            return {"mean": 0.0, "median": 0.0, "variance": 0.0, "stddev": 0.0}
        n = len(scores)
        mean_val = sum(scores) / n
        sorted_s = sorted(scores)
        median_val = sorted_s[n // 2]
        var_val = sum((x - mean_val) ** 2 for x in scores) / n
        stddev_val = math.sqrt(var_val)
        return {
            "mean": round(mean_val, 4),
            "median": round(median_val, 4),
            "variance": round(var_val, 4),
            "stddev": round(stddev_val, 4),
        }

    def compute_full_report(self, evaluations: List[Dict[str, Any]]) -> MetricReport:
        total = len(evaluations)
        accepted = sum(1 for e in evaluations if e.get("decision") == "ACCEPT")
        rejected = sum(1 for e in evaluations if e.get("decision") == "REJECT")
        borderline = sum(1 for e in evaluations if e.get("decision") == "BORDERLINE")

        dom_count, dom_pct = self.calculate_domain_leakage(evaluations)
        ctx_count, ctx_pct = self.calculate_context_leakage(evaluations)

        prec = self.calculate_semantic_precision(evaluations)
        rec = self.calculate_semantic_recall(evaluations)
        rqs = self.calculate_recommendation_quality(prec, dom_pct, ctx_pct)

        sim_scores = [e.get("semantic_similarity", 0.0) for e in evaluations]
        suit_scores = [e.get("suitability", 0.0) for e in evaluations]

        sim_dist = self.calculate_score_distribution(sim_scores)
        suit_dist = self.calculate_score_distribution(suit_scores)

        return MetricReport(
            total_evaluated=total,
            total_accepted=accepted,
            total_rejected=rejected,
            total_borderline=borderline,
            domain_leakage_count=dom_count,
            context_leakage_count=ctx_count,
            domain_leakage_pct=dom_pct,
            context_leakage_pct=ctx_pct,
            semantic_precision_pct=prec,
            semantic_recall_pct=rec,
            recommendation_quality_score=rqs,
            similarity_mean=sim_dist["mean"],
            similarity_stddev=sim_dist["stddev"],
            suitability_mean=suit_dist["mean"],
            suitability_stddev=suit_dist["stddev"],
        )
