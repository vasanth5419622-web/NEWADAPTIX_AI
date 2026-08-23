# ADAPTIX-FARM — Interactive Demonstration Guide

Follow these walkthroughs to demonstrate the key innovations of ADAPTIX-FARM.

---

## 🎬 Scenario 1: Complete Tomato Early Blight Workflow
1. Open the Dashboard at `http://127.0.0.1:8000`.
2. Click the preset button: **"🍅 Tomato Early Blight (Full Pipeline)"**.
3. Observe the pre-loaded image, field context (Coimbatore, Kharif), and symptoms query.
4. Click **"RUN ADAPTIX PIPELINE"**.
5. **Observe Execution:**
   - Pre-flight image quality check passes.
   - Route trace shows Open-weight model ($0.00) identifying crop species.
   - Commercial Model A (~$0.015) diagnosing *Alternaria solani* target spots.
   - RAG engine retrieving ICAR Bulletin #42 citations.
   - Commercial Model B Critic (~$0.009) conducting independent consistency verification.
   - Results tab displays **High Confidence (89%)**, **Verified status**, IPM checklist, and Text-to-Speech audio button.

---

## 🎬 Scenario 2: Multimodal Reasoning on Chilli Leaf Curl
1. Click the preset: **"🌶️ Chilli Leaf Curl (Complex Multimodal)"**.
2. Click **"RUN ADAPTIX PIPELINE"**.
3. **Observe Execution:**
   - Multi-Evidence Fusion correlates upward curling with whitefly vector activity.
   - RAG retrieves National Horticulture Board Chilli Crop Protection Manual.
   - Recommends vector suppression (yellow sticky traps, neem oil) and roguing.

---

## 🎬 Scenario 3: Unseen Dynamic Request (No Hardcoding)
1. Click the preset: **"✨ Unseen Dynamic Query"**.
2. Query: *“My chilli plant leaves are curling and showing pale patches. What should I check?”*
3. Click **"RUN ADAPTIX PIPELINE"**.
4. **Observe Execution:**
   - Planner dynamically decomposes the novel query into custom tasks without relying on hardcoded static rules.

---

## 🎬 Scenario 4: Poor Image Quality Gate (Fallback Demo)
1. Click the preset: **"⚠️ Poor Image Quality Gate (Fallback Demo)"**.
2. Click **"RUN ADAPTIX PIPELINE"**.
3. **Observe Execution:**
   - Deterministic Laplacian variance & resolution gate flags blurry image.
   - Haults downstream deep model calls immediately ($0.00 cost incurred).
   - Generates actionable user guidance: *“Hold the camera steady in daylight... capture a close-up (15-30cm) of the affected leaves.”*
