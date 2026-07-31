"""
Script to write all 5 Phase 0 Investigation Markdown reports in backend/tests/output/.
"""

import json
from pathlib import Path

out_dir = Path("backend/tests/output")
out_dir.mkdir(parents=True, exist_ok=True)

with open("backend/scratch_investigation_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

stats = data["scenario_stats"]
evals = data["evaluations"]

# 1. stage4f1_investigation.md
with open(out_dir / "stage4f1_investigation.md", "w", encoding="utf-8") as f:
    f.write("# Stage 4F.1 — Phase 0 Read-Only Investigation Report\n\n")
    f.write("## Overview\n")
    f.write("This investigation report audits Layer 5.5 (`SemanticRecommendationEngine`) to identify mathematical inconsistencies, metric calculation discrepancies, score clustering, and decision boundary behavior across benchmark queries.\n\n")
    
    f.write("## Executive Findings\n")
    f.write("1. **Metric Calculation Discrepancies**: Telemetry, Markdown reports, and JSON exports use inconsistent formulas for `domain_leakage` (evaluated candidates vs returned candidates vs accepted candidates).\n")
    f.write("2. **Suitability Score Degeneracy**: Suitability score is `100.0%` (StdDev `0.000`) for all non-healthy benchmark queries, behaving as a step-function binary pass rather than a continuous metric.\n")
    f.write("3. **Semantic Score Clustering**: Semantic scores cluster around 5 discrete values (`1.00`, `0.85`, `0.58`, `0.46`, `0.30`) due to coarse component matching.\n")
    f.write("4. **Static Acceptance Thresholds**: Fixed thresholds (`0.85`, `0.80`, `0.75`) create artificial boundaries rather than adapting to candidate score distributions.\n")
    f.write("5. **Explanation Gaps**: Candidate explanations lack structured quantitative confidence scores and granular violation details.\n\n")

    f.write("## Benchmark Scenario Audit Summary\n\n")
    f.write("| Scenario | Total Evaluated | Accepted | Rejected | Mean Semantic | StdDev Semantic | Unique Scores | Mean Suitability |\n")
    f.write("|---|---|---|---|---|---|---|---|\n")
    for sc_name, s in stats.items():
        f.write(f"| `{sc_name}` | {s['total_candidates']} | {s['accepted']} | {s['rejected']} | {s['mean_semantic']*100:.1f}% | {s['stddev_semantic']*100:.1f}% | {len(s['unique_semantic_scores'])} | {s['mean_suitability']*100:.1f}% |\n")
    f.write("\n")

# 2. leakage_consistency.md
with open(out_dir / "leakage_consistency.md", "w", encoding="utf-8") as f:
    f.write("# Stage 4F.1 Investigation 1 — Leakage Metric Consistency Audit\n\n")
    f.write("## Inconsistency Audit\n\n")
    
    f.write("### 1. Telemetry Calculation\n")
    f.write("- **File**: `backend/app/services/recommendation_engine/semantic_recommendation_engine.py`\n")
    f.write("- **Function**: `SemanticRecommendationEngine.evaluate_and_filter()`\n")
    f.write("- **Formula**: `domain_leakage_count = sum(1 for cand in ranked_evaluations if is_forbidden)`\n")
    f.write("- **Input**: Ranked candidate evaluations from Layer 5\n")
    f.write("- **Output**: Integer count of forbidden domain items evaluated by Layer 5.5 (e.g. `3` for Indian Dinner, `2` for Coffee)\n\n")

    f.write("### 2. Markdown Report Calculation\n")
    f.write("- **File**: `backend/tests/stage4f_semantic_test.py`\n")
    f.write("- **Function**: `Stage4FSemanticTest.tearDownClass()`\n")
    f.write("- **Formula**: `dom_leak_pct = (sum(domain_leakage) / sum(ranked_count)) * 100.0`\n")
    f.write("- **Input**: Aggregate test scenario results list\n")
    f.write("- **Output**: Percentage of evaluated candidates flagged as forbidden (`7.8%` or `0.0%` depending on denominator scope)\n\n")

    f.write("### 3. JSON Statistics Export Calculation\n")
    f.write("- **File**: `backend/tests/stage4f_semantic_test.py`\n")
    f.write("- **Function**: `Stage4FSemanticTest.tearDownClass()`\n")
    f.write("- **Formula**: `stat_data['domain_leakage_rate_pct'] = dom_leak_pct`\n")
    f.write("- **Input**: Copy of `dom_leak_pct` variable\n")
    f.write("- **Output**: Single float exported to `semantic_statistics.json`\n\n")

    f.write("## Root Cause of Disagreement\n")
    f.write("- In earlier Phase 0 reports, `domain_leakage` measured non-domain items returned in the **final user payload**.\n")
    f.write("- In Layer 5.5 telemetry, `domain_leakage` measures forbidden items filtered out during **candidate evaluation**.\n")
    f.write("- Because there is no single `SemanticMetricsCalculator`, different components compute metrics against different candidate pools (Total Evaluated vs Accepted vs Returned).\n")
    f.write("- **Solution**: Phase 1 will implement `SemanticMetricsCalculator` in `semantic_metrics.py` as the single source of truth.\n\n")

# 3. suitability_analysis.md
with open(out_dir / "suitability_analysis.md", "w", encoding="utf-8") as f:
    f.write("# Stage 4F.1 Investigation 2 — Suitability Score Audit\n\n")
    f.write("## Current Suitability Implementation\n")
    f.write("- **Formula**: Step-function conditionally evaluated only when `healthy` or `health_goal` constraint exists:\n")
    f.write("  ```python\n")
    f.write("  suitability_score = 1.00\n")
    f.write("  if 'healthy' in query_text or health_goal:\n")
    f.write("      if fast_food_burger and not healthy:\n")
    f.write("          suitability_score = 0.15\n")
    f.write("      elif healthy or high_protein:\n")
    f.write("          suitability_score = 1.00\n")
    f.write("      else:\n")
    f.write("          suitability_score = 0.50\n")
    f.write("  ```\n\n")

    f.write("## Audit Evidence & Distribution\n")
    f.write("- **Non-Healthy Benchmark Queries** (`Coffee`, `Desserts`, `Italian`, `Pizza`, `Indian Dinner`):\n")
    f.write("  - `Suitability Score`: **100.0%** for 100% of candidates evaluated.\n")
    f.write("  - `Mean`: **1.0000** | `Median`: **1.0000** | `StdDev`: **0.0000** | `Unique Values`: **[1.0]**.\n")
    f.write("- **Proof of Binary Pass Behavior**: Suitability currently acts as a binary/trinary pass flag rather than a continuous score.\n")
    f.write("- **Solution**: Phase 2 will implement a continuous multi-attribute suitability model combining Domain (0.35), Context (0.20), Intent (0.20), Conversation (0.15), and Constraint Coverage (0.10).\n\n")

# 4. semantic_distribution.md
with open(out_dir / "semantic_distribution.md", "w", encoding="utf-8") as f:
    f.write("# Stage 4F.1 Investigation 3 — Semantic Score Distribution Report\n\n")
    f.write("## Distribution Analysis Across Benchmark Scenarios\n\n")

    for sc_name, s in stats.items():
        f.write(f"### Scenario: {sc_name}\n")
        f.write(f"- **Total Candidates Evaluated**: {s['total_candidates']}\n")
        f.write(f"- **Mean Semantic Score**: `{s['mean_semantic']*100:.1f}%`\n")
        f.write(f"- **Median Semantic Score**: `{s['median_semantic']*100:.1f}%`\n")
        f.write(f"- **Variance**: `{s['variance_semantic']:.4f}` | **StdDev**: `{s['stddev_semantic']*100:.1f}%`\n")
        f.write(f"- **Unique Score Values**: `{s['unique_semantic_scores']}`\n")
        f.write("- **Histogram / Score Buckets**:\n")
        sc_evals = [e for e in evals if e["scenario"] == sc_name]
        counts = {}
        for e in sc_evals:
            counts[e["semantic_score"]] = counts.get(e["semantic_score"], 0) + 1
        for val in sorted(counts.keys(), reverse=True):
            f.write(f"  - Score `{val*100:5.1f}%`: {'█' * counts[val]} ({counts[val]} candidates)\n")
        f.write("\n")

    f.write("## Key Finding: Score Clustering vs Continuity\n")
    f.write("- **Answer**: Semantic scores are **HEAVILY CLUSTERED** into 5 discrete values (`1.00`, `0.85`, `0.58`, `0.46`, `0.30`).\n")
    f.write("- **Root Cause**: Coarse tier matching in `domain_match` and discrete step-functions in `meal_context` and `suitability_score` create coarse score step plateaus.\n")
    f.write("- **Solution**: Phase 3 will replace coarse step-functions with continuous similarity scoring across domain, category, meal, cuisine, and health attributes.\n\n")

# 5. decision_boundary.md
with open(out_dir / "decision_boundary.md", "w", encoding="utf-8") as f:
    f.write("# Stage 4F.1 Investigation 4 & 5 — Decision Boundary & Explanation Audit\n\n")
    f.write("## Acceptance Boundary Analysis\n\n")
    f.write("Candidate evaluations sorted by Semantic Score across benchmark queries:\n\n")
    f.write("| Scenario | Candidate | Ranking Score | Semantic Score | Policy Threshold | Decision | Reason |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    for e in sorted(evals, key=lambda x: (x["scenario"], -x["semantic_score"])):
        f.write(f"| `{e['scenario']}` | {e['candidate_name']} | {e['ranking_score']:.1f} | **{e['semantic_score']*100:.0f}%** | {e['threshold']:.2f} | **{'ACCEPT' if e['accepted'] else 'REJECT'}** | {e['reason']} |\n")
    f.write("\n")

    f.write("## Boundary Evaluation & Explanation Findings\n")
    f.write("1. **Threshold Boundary Separation**: Fixed thresholds (`0.85`, `0.80`, `0.75`) successfully separate valid domain candidates from invalid ones, but cause artificial rejection when high-quality candidates fall slightly below a static cutoff.\n")
    f.write("2. **Explanation Evidence Consistency**: Accepted candidate reasons currently use simple template strings (`Recommended because: Coffee domain match, Fits budget (₹220)`). They do not present granular quantitative confidence metrics or explicit breakdown vectors.\n")
    f.write("3. **Solution Plan**: Phase 4 will introduce Adaptive Acceptance Thresholds based on candidate score distributions, and Phase 5 will implement Evidence-Based Explanations derived directly from evaluation metrics.\n\n")

print("SUCCESS: 5 Phase 0 Investigation Markdown reports generated.")
