# ADAPTIX-FARM
### Adaptive Multimodal AI for Accessible Crop Intelligence
> **“Show the crop. Speak naturally. Get verified advice.”**

ADAPTIX-FARM is an agentic, multimodal AI crop pathology and agricultural advisory platform developed for the **FarmwiseAI Task 1** challenge. Unlike single-query prediction tools, ADAPTIX-FARM builds an autonomous, multi-stage reasoning pipeline: it inspects image quality, dynamically plans tasks, routes queries across open-weight and commercial AI models based on multi-objective scoring (capability, latency, cost), retrieves authoritative extension bulletins (RAG), fuses multi-modal evidence, and conducts independent critic verification before delivering actionable advisory.

---

## 🌾 Core Features & Capabilities

1. **Pre-flight Image Quality Gate:**
   Deterministic Laplacian variance blur detection and photometric analysis (exposure/contrast/resolution) prevent unreadable photos from wasting model calls and provide actionable feedback.
2. **Dynamic Task Planner & Decomposition:**
   Decomposes farmer queries into explicit steps: `crop_identification`, `symptom_analysis`, `advisory_retrieval`, `evidence_fusion`, `verification`, `recommendation`. Reusable across any crop or unseen condition.
3. **Three-Tier Adaptive Model Router:**
   - **Open-Weight / Smaller Model (`qwen-vl-small`):** Low-cost, fast initial taxonomy and crop identification ($0.00 / 280ms).
   - **Commercial Model A (`gpt-4o-mini`):** Deep multimodal reasoning for ambiguous lesions and complex symptoms (~$0.015 / 1450ms).
   - **Commercial Model B (`claude-3-5-sonnet`):** Independent critic and consistency verifier (~$0.009 / 920ms).
4. **Agricultural RAG Advisory Engine:**
   Extracts, chunks, and indexes ICAR, TNAU, and State University extension bulletins into a semantic vector store, providing verified citations with page numbers.
5. **Multi-Evidence Fusion & Conflict Detector:**
   Cross-references visual pathology, RAG advisory guidelines, and field environmental context (growth stage, location, season) to catch agronomic inconsistencies.
6. **Independent Critic & Confidence Engine:**
   Calculates calibrated composite confidence scores (High, Moderate, Low). Flags ambiguous cases as *“Requires Review”* and prevents false certainties.
7. **Natural Voice Interaction (English & Tamil):**
   Speech-to-Text for farmer queries and Text-to-Speech audio advisory playback.
8. **Observability & Audit Trail:**
   Live route trace inspection, step-by-step latency breakdown, estimated API cost tracking, and SQLite persistence.

---

## 🏗️ Architecture Overview

```
                          USER
                           ↓
             [ INPUT / IMAGE QUALITY CHECK ]
                           ↓
                [ PLANNER / ORCHESTRATOR ]
                           ↓
                  [ TASK DECOMPOSITION ]
                           ↓
                [ ADAPTIVE MODEL ROUTER ]
                           ↓
         ┌─────────────────┼─────────────────┐
         ↓                 ↓                 ↓
   Open-Weight       Commercial A      Commercial B     Agricultural RAG
   Small Model       Deep Reasoning       Critic        Vector Store (PDFs)
         └─────────────────┬─────────────────┘
                           ↓
                [ MULTI-EVIDENCE FUSION ]
                           ↓
                 [ VERIFIER / CRITIC ]
                           ↓
               [ CONFIDENCE EVALUATION ]
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
         HIGH CONF.                  LOW CONF.
              │                         ↓
              │                    [ ESCALATION ]
              │             (Stronger Model / Field Review)
              └────────────┬────────────┘
                           ↓
                 [ FINAL RECOMMENDATION ]
                           ↓
                    [ TEXT + VOICE ]
```

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.10+
* Modern Web Browser (Chrome, Edge, Firefox, Safari)

### Installation & Launch

1. **Clone or Navigate to the directory:**
   ```bash
   cd C:\Users\ELCOT\Desktop\farmwiseai
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Start the Unified Server:**
   ```bash
   python backend/app/main.py
   ```
   *Or run the helper script:*
   ```bash
   .\scripts\run_app.bat
   ```

4. **Access the Farmer Dashboard:**
   Open your browser and navigate to:
   👉 **`http://127.0.0.1:8000`**

---

## 🧪 Testing & Verification

Run the automated pytest test suite covering all agentic modules:
```bash
python -m pytest -v
```
*Result: 16 passed unit and integration tests across Image Quality, Planner, Router, RAG, Fusion, Critic, Confidence, and REST APIs.*

---

## 📖 Demonstration Workflows

1. **Tomato Early Blight (Full Pipeline Demo):**
   - Click preset **"🍅 Tomato Early Blight"** on the Dashboard.
   - Executes image quality check -> Open model crop ID -> Commercial Model A pathology -> RAG retrieval -> Commercial Model B critic -> High Confidence Verified recommendation with audio TTS.
2. **Chilli Leaf Curl (Multimodal Reasoning Demo):**
   - Click preset **"🌶️ Chilli Leaf Curl"**.
   - Demonstrates vector management guidelines and sucking pest IPM.
3. **Unseen Dynamic Request Demo:**
   - Click preset **"✨ Unseen Dynamic Query"** (*“My chilli plant leaves are curling with pale patches...”*).
   - Generates plan dynamically without hard-coded rules.
4. **Poor Image Quality Fallback Demo:**
   - Click preset **"⚠️ Poor Image Quality Gate"**.
   - Triggers Laplacian blur gate, halting expensive model calls and prompting for a focused, well-lit photo.

---

## 🛡️ Responsible AI Framework
* **Non-Prescriptive Language:** Always uses *“Possible condition”*, *“AI-assisted assessment”*, and *“System confidence score”*.
* **No Autonomous Chemical Application:** Recommends integrated pest management and consultation with local agricultural extension officers.
* **Traceable Citations:** All guidance references verified agricultural university bulletins with page citations.

---

## 📂 Project Structure

```text
farmwiseai/
├── backend/
│   ├── app/
│   │   ├── api/          # REST API endpoints (/api/analyze, /api/documents, etc.)
│   │   ├── core/         # Config, structured logging, SQLite persistence
│   │   ├── models/       # Model schemas & database models
│   │   ├── schemas/      # Shared Pydantic data schemas
│   │   ├── services/
│   │   │   ├── confidence/  # Calibrated confidence & risk engine
│   │   │   ├── fallback/    # Fallback & escalation handlers
│   │   │   ├── image/       # Laplacian blur & photometric quality gate
│   │   │   ├── models/      # OpenWeight, Commercial A & B, Mock providers
│   │   │   ├── planner/     # Dynamic planner & task decomposition
│   │   │   ├── rag/         # PDF parser, semantic vector store, citations
│   │   │   ├── router/      # Adaptive model router with multi-objective scoring
│   │   │   ├── verifier/    # Multi-evidence fusion & independent critic
│   │   │   └── voice/       # Speech-to-Text & Text-to-Speech engine
│   │   └── main.py       # FastAPI application entrypoint
│   ├── tests/            # Pytest test suite (16 comprehensive tests)
│   └── requirements.txt  # Backend dependencies
├── frontend/
│   ├── index.html        # Responsive Farmer Dashboard SPA
│   ├── public/
│   └── src/
│       ├── app.js        # Dynamic UI, voice recognition, charts, demo presets
│       └── styles.css    # Custom styles & animations
├── data/
│   ├── documents/        # Uploaded advisory PDFs
│   ├── images/           # Uploaded crop photographs
│   └── vectorstore/      # Vector index & JSON embeddings
├── docs/                 # ARCHITECTURE.md, API.md, SETUP.md, TESTING.md, DEMO.md
├── scripts/              # Helper launcher scripts
├── .env.example          # Environment variables template
├── pytest.ini            # Test configuration
└── README.md
```
