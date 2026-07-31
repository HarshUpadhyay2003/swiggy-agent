# Swiggy AI Copilot — Release Gate Checklist (Stage RC-1)

Before merging into `main` and tagging release `v1.0-demo`, all gates must be verified:

- [x] **Repository Cleanup:** Scratch files, legacy tests, and old output logs organized into `archive/`.
- [x] **Code Quality:** Unused imports and dead code removed; zero syntax errors.
- [x] **Configuration:** Centralized settings in `backend/config/settings.py`.
- [x] **Health & Version APIs:** `/health` returns uptime and status; `/version` returns build metadata.
- [x] **Automated Tests:** `python backend/tests/run_backend_tests.py` passes (41/41 tests OK).
- [x] **Calibration Tests:** `python backend/tests/stage4f1_calibration_test.py` passes (9/9 tests OK).
- [x] **Documentation Suite:** 11 documentation markdown files complete in `docs/`.
- [x] **Manual Acceptance Scenarios:** 8 representative conversational flows verified via frontend UI.
- [x] **Backend Server Boot:** `uvicorn app.main:app` starts without warnings or errors.
