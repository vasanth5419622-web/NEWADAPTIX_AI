# ADAPTIX-FARM — Setup & Installation Guide

## 1. Environment Setup

### 1.1 Requirements
* Python 3.10, 3.11, or 3.12
* Windows, Linux, or macOS

### 1.2 Virtual Environment & Dependencies
```bash
# Navigate to project directory
cd C:\Users\ELCOT\Desktop\farmwiseai

# Install Python requirements
pip install -r backend/requirements.txt
```

---

## 2. Environment Variables Configuration

Copy `.env.example` to `.env` to configure external commercial AI model keys (optional):

```env
APP_ENV=development
PORT=8000
HOST=127.0.0.1
DEBUG=true

# Model 1: Open-Weight Model (Local / Ollama / HF)
OPEN_MODEL_PROVIDER=mock
OPEN_MODEL_NAME=qwen-vl-small

# Model 2: Commercial Model A (Deep Reasoning)
COMMERCIAL_MODEL_A_PROVIDER=mock
COMMERCIAL_MODEL_A_NAME=gpt-4o-mini
COMMERCIAL_MODEL_A_API_KEY=

# Model 3: Commercial Model B (Independent Critic)
COMMERCIAL_MODEL_B_PROVIDER=mock
COMMERCIAL_MODEL_B_NAME=claude-3-5-sonnet
COMMERCIAL_MODEL_B_API_KEY=
```

> **Note:** If API keys are not provided, ADAPTIX-FARM automatically operates in its high-fidelity agronomic simulation mode, enabling seamless offline evaluation and testing without vendor lock-in.

---

## 3. Running the Server

Start the unified FastAPI server:
```bash
python backend/app/main.py
```
Or use the launcher script:
```bash
.\scripts\run_app.bat
```

Access the application in your browser:
**`http://127.0.0.1:8000`**
