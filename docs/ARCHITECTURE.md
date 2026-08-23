# ADAPTIX-FARM — Architectural Design Document

## 1. System Philosophy
ADAPTIX-FARM replaces monolithic, hard-coded agricultural diagnosis pipelines with an **adaptive, multi-agent orchestration architecture**. The system dynamically plans tasks, selects models based on multi-objective optimization, retrieves authoritative university bulletins (RAG), and conducts independent critic verification before delivering actionable advice.

---

## 2. Multi-Tier Model Routing

$$\text{Routing Score} = \text{Capability} + \text{Confidence} - \text{Latency Penalty} - \text{Cost Penalty} + \text{Availability}$$

| Model Tier | Model Name | Role | Latency | Estimated Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Open-Weight)** | `qwen-vl-small` / Local Classifier | Fast crop taxonomy & leaf localization | ~280 ms | $0.00000 |
| **Tier 2 (Commercial A)** | `gpt-4o-mini` / Claude 3.5 | Deep multimodal pathology reasoning | ~1450 ms | ~$0.01450 |
| **Tier 3 (Commercial B)** | `claude-3-5-sonnet` | Independent critic & hallucination verifier | ~920 ms | ~$0.00920 |
| **RAG Tool** | Semantic Vector Store | Extension literature search & citation | ~180 ms | $0.00050 |

---

## 3. Core Modules

### 3.1 Pre-Flight Image Quality Gate (`backend/app/services/image/quality.py`)
* Computes discrete Laplacian variance on grayscale foliage to evaluate blur sharpness.
* Evaluates luminance mean and standard deviation to detect extreme exposure conditions.
* Evaluates image resolution against a $150 \times 150$ px threshold.
* Rejects poor photos early, saving compute and providing immediate instructions to the farmer.

### 3.2 Dynamic Agricultural Planner (`backend/app/services/planner/planner.py`)
* Creates an explicit `ExecutionPlan` consisting of sequential `TaskItem` objects.
* Adaptively accounts for image presence, stated user context, and query intent.

### 3.3 Agricultural RAG & Vector Engine (`backend/app/services/rag/`)
* Ingests ICAR, TNAU, and State University extension bulletins in PDF or Markdown format.
* Tokenizes and computes semantic cosine similarity embeddings.
* Attaches exact source citations with page numbers to all recommendations.

### 3.4 Multi-Evidence Fusion & Conflict Detector (`backend/app/services/verifier/fusion.py`)
* Cross-references visual findings, RAG advisory guidelines, and environmental context.
* Flags inconsistencies (such as seedling stage mismatch with late-season foliar diseases).

### 3.5 Independent Critic & Confidence Engine (`backend/app/services/confidence/engine.py`)
* Formulates a composite score:
  $$C = 0.30 \cdot M_{\text{conf}} + 0.25 \cdot E_{\text{agree}} + 0.20 \cdot Q_{\text{img}} + 0.15 \cdot V_{\text{critic}} + 0.10 \cdot C_{\text{ctx}}$$
* Calibrates output to **High**, **Moderate**, or **Low** confidence, triggering autonomous escalation when needed.
