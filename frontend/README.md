# VoxShield Frontend Dashboard 💻

> **React + Vite + TypeScript + Tailwind CSS UI**  
> *Primary Developer: Developer 2 (Frontend & UX Lead)*

---

## 🎨 Features & Capabilities

- **Interactive Microphone Recorder**: Web Audio API recorder with live volume level indicator.
- **Drag-and-Drop Audio Uploader**: Drag & drop or sample picker for `.wav`, `.mp3`, `.flac`, `.m4a` files.
- **Waveform Canvas Visualizer**: Dynamic HTML5 canvas waveform renderer.
- **Risk Assessment Meter**: Radial/linear threat gauge showing synthetic score, replay score, and status pill (`SAFE`, `SUSPICIOUS`, `HIGH_RISK`).
- **Isolated Mock API Mode**: Built-in mock API service layer (`services/mockApi.ts`) enabling full UI testing without running the Python backend.

---

## ⚡ Quick Start

```bash
# Install dependencies
npm install

# Create environment file from example
cp .env.example .env

# Run Vite dev server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🔄 Switching from Mock API to Live FastAPI

To connect the frontend to Developer 1's backend:
1. Update `.env`:
   ```env
   VITE_USE_MOCK_API=false
   VITE_API_BASE_URL=http://localhost:8000
   ```
2. Restart Vite dev server (`npm run dev`).
