# VoxShield 🛡️

> **AI-Powered Voice Impersonation & Deepfake Voice Detection System**  
> *Developed for Smart India Hackathon (SIH)*

VoxShield is an enterprise-grade AI audio security system designed to combat deepfake voice impersonation, synthetic speech synthesis, and audio replay attacks. By combining cutting-edge deep learning anti-spoofing models with digital signal processing (DSP) acoustic feature analysis and a contextual risk evaluation engine, VoxShield protects voice authentication channels, call centers, and financial transactions in real time.

---

## 🎯 Key Capabilities

- **Deepfake & Synthetic Speech Detection**: Neural network classification detecting subtle acoustic artifacts in AI-generated voice clones (ElevenLabs, Bark, VALL-E, Tacotron, WaveNet, etc.).
- **Acoustic Replay Attack Detection**: Spectral frequency analysis identifying room reverberation, microphone impulse responses, and background transducer noise typical of recorded audio replays.
- **Contextual Risk Engine**: Dynamic scoring system blending synthetic probabilities and replay vectors into actionable risk states (`SAFE`, `SUSPICIOUS`, `HIGH_RISK`).
- **Developer-First Architecture**: Decoupled React + FastAPI stack with built-in mock modes enabling parallel frontend and backend development.
- **Extensible Verification Pipeline**: Standardized schema structured for future biometric speaker matching and real-time WebSocket audio streaming.

---

## 🏗 Architecture Overview

```text
Microphone / Audio File Upload
             │
             ▼
    React + Vite Frontend (Dashboard & Audio Visualizer)
             │
             ▼ REST / WebSocket
    FastAPI Security Backend
             │
   ┌─────────┴────────────────────────┐
   │                                  │
   ▼                                  ▼
Acoustic Audio Processor      Deepfake AI Anti-Spoofing
(Librosa / Torchaudio / DSP)  (PyTorch / Neural Classifier)
   │                                  │
   └─────────┬────────────────────────┘
             │
             ▼
   Replay Attack Analyzer
             │
             ▼
    Contextual Risk Engine
             │
             ▼
   JSON Analysis Response ➔ Frontend Dashboard UI
```

---

## 🛠 Technology Stack

### Frontend (Developer 2)
- **Framework**: React 18 + Vite + TypeScript
- **Styling**: Tailwind CSS + Lucide Icons + HSL Design System
- **State & HTTP**: Axios, React Hooks, Web Audio API
- **Visualization**: HTML5 Canvas Waveform Renderer

### Backend & AI (Developer 1)
- **API Engine**: FastAPI + Uvicorn + Pydantic v2
- **AI/ML Runtime**: PyTorch, Torchaudio, Scikit-learn, NumPy
- **Audio DSP**: Librosa, SciPy
- **Testing**: PyTest, HTTPX

---

## 📂 Repository Structure

```text
voxshield/
├── frontend/             # React UI, Components, Audio Recording & Mock API Layer
│   ├── src/
│   │   ├── components/   # Visualizers, Risk Gauges, Audio Uploader, Recorder
│   │   ├── pages/        # Dashboard & Analytics Pages
│   │   ├── hooks/        # React Hooks for Audio Processing
│   │   ├── services/     # API Client & Mock Service
│   │   ├── types/        # TypeScript Schemas
│   │   └── utils/        # Audio Helpers
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
│
├── backend/              # FastAPI Application, AI Models & Risk Engine
│   ├── app/
│   │   ├── api/          # Route Handlers (/health, /analyze, /stream)
│   │   ├── core/         # Configuration & Settings
│   │   ├── schemas/      # Pydantic Schemas
│   │   ├── services/     # Audio DSP, Anti-Spoofing ML & Risk Engine
│   │   └── main.py       # FastAPI Entrypoint
│   ├── tests/            # Automated PyTest Test Suite
│   ├── models/           # Pre-trained Model Weights Directory (.gitkeep)
│   ├── data/             # Sample Audio & Test Datasets (.gitkeep)
│   ├── requirements.txt
│   └── README.md
│
├── docs/                 # Architectural Specs & Hackathon Materials
│   ├── architecture.md   # Component Specs & Audio Data Flow
│   ├── api-contract.md   # OpenAPI Specifications
│   ├── development-plan.md # Development Roadmap & Sprints
│   └── demo-flow.md      # SIH Presentation Script
│
├── .github/workflows/    # CI/CD Workflows
├── CONTRIBUTING.md       # Team Git Workflow & Coding Standards
├── LICENSE               # MIT License
└── README.md
```

---

## ⚡ Quick Start Guide

### Prerequisites
- **Node.js**: v18.x or higher
- **Python**: 3.10 or higher
- **Git**: 2.x

---

### 1️⃣ Setting Up the Backend (Developer 1)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file from example
cp .env.example .env

# Run FastAPI development server
uvicorn app.main:app --reload --port 8000
```

Verify backend health check at: `http://localhost:8000/api/v1/health`

---

### 2️⃣ Setting Up the Frontend (Developer 2)

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file from example
cp .env.example .env

# Start Vite development server
npm run dev
```

Open browser at `http://localhost:5173`.  
*By default, `VITE_USE_MOCK_API=true` is enabled so the frontend works immediately without requiring the backend!*

---

## 👥 Team Responsibilities

| Role | Developer | Responsibilities | Primary Folder |
| :--- | :--- | :--- | :--- |
| **Backend & AI Lead** | Developer 1 | FastAPI Endpoints, PyTorch Model Integration, Feature Extraction (MFCC/LFCC), Replay DSP & Risk Engine Logic | `backend/` |
| **Frontend & UX Lead** | Developer 2 | React Application, Tailwind CSS Styling, Microphone Web Audio API, Result Dashboards, Mock API & API Integration | `frontend/` |

---

## 📡 API Contract Summary

### Health Check
`GET /api/v1/health`  
Returns `{"status": "ok"}`

### Audio Analysis Endpoint
`POST /api/v1/analyze` (Form Data: `file: UploadFile`)

```json
{
  "synthetic_score": 0.91,
  "replay_score": 0.73,
  "speaker_match": null,
  "risk_score": 0.89,
  "status": "HIGH_RISK",
  "reasons": [
    "Synthetic voice characteristics detected",
    "Possible replay characteristics detected"
  ]
}
```

*Status options: `SAFE`, `SUSPICIOUS`, `HIGH_RISK`*

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
