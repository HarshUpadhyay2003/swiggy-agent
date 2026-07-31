# Swiggy AI Copilot — Testing Guide (Stage RC-1)

## Overview
The backend includes a comprehensive testing framework spanning unit tests, integration tests, stage-specific pipeline regression tests, and calibration suites.

---

## Automated Test Execution

### 1. Run Master Backend Test Suite
Executes unit tests and integration tests across catalog, retrieval, ranking, validator, and checkout.
```bash
python backend/tests/run_backend_tests.py
```

### 2. Run Stage 4F.1 Semantic Calibration Suite
Executes semantic evaluator, decision engine, adaptive threshold calibration, and candidate integrity assertions.
```bash
python backend/tests/stage4f1_calibration_test.py
```

### 3. Run Recommendation Pipeline Suite
Executes end-to-end multi-turn recommendation flow test scenarios.
```bash
python backend/tests/recommendation_pipeline_test.py
```

---

## Diagnostic Scripts
Located in `backend/tests/diagnostics/`:
- `ranking_deep_audit.py` — Evaluates score variance, ties, and component score weight distributions.
- `stage4b_investigation.py` — Verifies constraint lifecycle transitions.
- `run_smoke_test.py` — Quick API verification.
