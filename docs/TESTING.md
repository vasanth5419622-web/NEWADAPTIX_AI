# ADAPTIX-FARM — Testing Strategy & Verification Guide

ADAPTIX-FARM includes an automated test suite verifying all 16 core requirements of the FarmwiseAI Task 1 proposal.

---

## 1. Running Automated Tests

Run the complete test suite using pytest:
```bash
python -m pytest -v
```

---

## 2. Test Coverage Breakdown

| Test File | Target Module | Description |
| :--- | :--- | :--- |
| `test_image_quality.py` | Image Quality Checker | Tests Laplacian variance blur detection & minimum resolution gate. |
| `test_planner.py` | Agricultural Planner | Tests dynamic task decomposition and unseen request planning. |
| `test_router.py` | Adaptive Model Router | Tests model tier selection based on task type and cost/latency scoring. |
| `test_rag.py` | Vector Advisory Engine | Tests semantic search and extension bulletin citation retrieval. |
| `test_fusion_verifier.py` | Fusion & Critic Verifier | Tests multi-evidence agreement and independent critic validation. |
| `test_confidence.py` | Confidence Engine | Tests composite confidence scoring across High, Moderate, and Low tiers. |
| `test_orchestrator.py` | Master Orchestrator | End-to-end integration test verifying full agentic execution path. |
| `test_api.py` | FastAPI REST Endpoints | Tests `/api/health`, `/api/analyze/text`, `/api/documents/list`, `/api/metrics`. |

All 16 tests execute deterministically and run in under 3 seconds.
