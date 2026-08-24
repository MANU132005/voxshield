# VoxShield Hackathon Development Roadmap

This document outlines the phased development roadmap for the VoxShield project during the Smart India Hackathon (SIH).

---

## 📅 Roadmap Overview

```
Phase 1: Foundation & Scaffold (Current)
  ├── Setup Repo Structure & CI/CD Pipeline
  ├── Create API Specifications & Pydantic Schemas
  ├── Develop Frontend UI Shell & Mock Service Engine
  └── Implement Minimal FastAPI Backend with Health & Mock Analysis

Phase 2: Core Engine Development (Parallel Tracks)
  ├── Developer 1 (Backend / AI):
  │     ├── Implement LFCC/MFCC Audio Feature Extraction Pipeline
  │     ├── Train / Integrate PyTorch Synthetic Voice Classifier
  │     ├── Implement Room Reverberation & Spectral Replay Analysis
  │     └── Develop Dynamic Risk Engine Scoring Logic
  │
  └── Developer 2 (Frontend / UX):
        ├── Enhance Audio Recorder with Web Audio API Spectrogram
        ├── Implement Interactive Risk Meters & Dynamic Visualizers
        ├── Build Audio Comparison & Forensic Breakdown Views
        └── Connect Frontend Service Layer to Live FastAPI Endpoints

Phase 3: Integration & Testing
  ├── End-to-End API Integration (Mock ➔ Live FastAPI)
  ├── Edge-case Testing (Noisy Audio, Different Formats, Silence)
  └── Performance Tuning (< 500ms Latency Benchmark)

Phase 4: SIH Final Demo Polish
  ├── Demo Recording & Backup Audio Sample Curation
  ├── Live Pitch Deck Preparation
  └── SIH Presentation Script Alignment
```

---

## 🎯 Phase 1 Goals Checklist

- [x] Repository created with standardized structure (`frontend/`, `backend/`, `docs/`)
- [x] API Contract defined in `docs/api-contract.md`
- [x] Mock API service created for frontend preview (`frontend/src/services/mockApi.ts`)
- [x] FastAPI base application running with `/api/v1/health` and `/api/v1/analyze`
- [x] Clean README and git workflows (`CONTRIBUTING.md`, `ci.yml`)
