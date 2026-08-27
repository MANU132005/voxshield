# VoxShield Master Production Deployment Plan

**Project**: VoxShield AI Voice Security & Anti-Spoofing System  
**Branch**: `feature/backend-ai`  
**Production Checkpoint**: `backend/models/asvspoof2019_la_recovery_exp01.pt`  
**Checkpoint SHA-256**: `f745df8fbab5351153c55a579d6a35f8cce0bcc4c3f2bcdfe47ba516348f9a06`  
**Target Architecture**: Vercel (Frontend) + Production Python Server (FastAPI + PyTorch Backend)  
**Date**: 2026-08-27  

---

## 1. End-to-End System Deployment Architecture

```
                                HTTPS
[Browser Client] ------------------------------------> [Vercel CDN / React 18 Frontend]
       |                                                         |
       | POST /api/v1/analyze (Audio Payload)                   | VITE_API_BASE_URL
       v                                                         v
[Production FastAPI Backend] <------------------------------------+
       |
       +---> 1. Audio Preprocessing (PySoundFile + SciPy Resample to 16kHz Mono)
       +---> 2. Spectrogram Feature Extractor (Log-Mel 80x300, Z-Score Normalization)
       +---> 3. PyTorch Neural Engine (VoiceAntiSpoofingResNet in eval() mode)
       +---> 4. Single-STFT Acoustic Replay DSP Engine
       +---> 5. Multi-Modal Threat Risk Evaluator + Forensic Intelligence Engine
       v
[AnalysisResponse JSON Result] -----------------------> [Frontend ResultCard UI]
```

---

## 2. Component Configuration Specifications

### A. Frontend Production Build (Vercel)
- **Root Directory**: `frontend/`
- **Build Command**: `npm run build` (`tsc && vite build`)
- **Output Directory**: `frontend/dist`
- **Environment Variables**:
  - `VITE_API_BASE_URL`: `https://<production-backend-domain>` (HTTPS Production Backend URL)
  - `VITE_USE_MOCK_API`: `false`
- **Vercel Configuration (`vercel.json`)**: Configured at root for monorepo routing to `frontend/`.

### B. Backend Production Server (FastAPI + Uvicorn)
- **Root Directory**: `backend/`
- **Startup Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Dependencies**: `pip install -r backend/requirements.txt` (`fastapi`, `uvicorn`, `torch`, `soundfile`, `scipy`, `pydantic-settings`, `python-multipart`)
- **Model Checkpoint**: Loads `models/asvspoof2019_la_recovery_exp01.pt` (SHA-256: `f745df8f...`)
- **Environment Variables**:
  - `ENVIRONMENT`: `production`
  - `DEBUG`: `false`
  - `CORS_ORIGINS`: `["https://voxshield.vercel.app", "https://<your-vercel-domain>.vercel.app"]`
  - `MODEL_PATH`: `models/asvspoof2019_la_recovery_exp01.pt`

---

## 3. Planned Deployment Implementation Steps (Phases 1–17)

1. **Phase 1**: Architecture & Pre-Deployment Audit
2. **Phase 2**: Frontend Environment Configuration (`VITE_API_BASE_URL`)
3. **Phase 3**: Backend Portable Path & Production Uvicorn Entry Point Audit
4. **Phase 4**: Checkpoint SHA-256 Hash Verification (`f745df8f...`)
5. **Phase 5**: Production CORS Hardening
6. **Phase 6**: Health & Readiness Probe Verification
7. **Phase 7**: Backend Deployment Setup & Environment Variables
8. **Phase 8**: Real Audio Production Inference Benchmark Test
9. **Phase 9**: Frontend Vercel Deployment Configuration (`vercel.json`)
10. **Phase 10 & 11**: Real End-to-End Browser $\rightarrow$ Backend Test Verification
11. **Phase 12**: API Failure Handling Verification
12. **Phase 13**: Security & HTTPS Audit
13. **Phase 14**: Lightweight Performance Latency Measurement
14. **Phase 15**: Full Pytest Regression Suite Execution (`206 / 206 PASS`)
15. **Phase 16**: Clean Git Commit & Push
16. **Phase 17**: Final Deployment Audit Report Generation (`PRODUCTION_DEPLOYMENT_AUDIT.md`)
