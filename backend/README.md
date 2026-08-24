# VoxShield Backend Engine 🐍

> **FastAPI Backend, AI Anti-Spoofing & Audio Processing Services**  
> *Primary Developer: Developer 1 (Backend & AI Lead)*

---

## 🏗 Architecture & Modules

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py        # GET /api/v1/health
│   │   │   ├── analyze.py       # POST /api/v1/analyze
│   │   │   └── stream.py        # WS /api/v1/stream
│   │   └── __init__.py
│   ├── core/
│   │   └── config.py            # Pydantic Settings & CORS
│   ├── schemas/
│   │   └── analysis.py          # Pydantic Input/Output Specs
│   ├── services/
│   │   ├── audio/
│   │   │   └── processor.py     # Librosa/FFmpeg Spectrogram Feature Extraction
│   │   ├── anti_spoofing/
│   │   │   └── detector.py      # PyTorch Model Inference (TODO: Integrate Weights)
│   │   ├── replay_detection/
│   │   │   └── dsp.py           # Reverberation & Spectral Decay DSP Logic
│   │   └── risk_engine/
│   │       └── evaluator.py     # Aggregated Risk Scoring Logic
│   └── main.py                  # FastAPI App Entrypoint
├── tests/                       # PyTest Suite
├── models/                      # Trained .pt/.pth Model Files (.gitkeep)
├── data/                        # Local Audio Test Samples (.gitkeep)
├── requirements.txt
└── .env.example
```

---

## ⚡ Quick Start

```bash
# 1. Create Python virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables
cp .env.example .env

# 5. Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```

---

## 🧪 Running Automated Tests

```bash
pytest
```

---

## 🛠 Integration TODOs for Developer 1

- [ ] `app/services/anti_spoofing/detector.py`: Load trained PyTorch model `.pt` file from `models/` directory.
- [ ] `app/services/audio/processor.py`: Complete LFCC/MFCC feature extraction functions.
- [ ] `app/services/replay_detection/dsp.py`: Tune FFT decay thresholds for room reverberation classification.
