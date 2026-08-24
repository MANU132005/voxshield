# VoxShield SIH Live Presentation & Demo Flow Script

This script provides the step-by-step walkthrough for presenting VoxShield to hackathon judges.

---

## 🎬 Presentation Script & Walkthrough

### 1. Introduction (30 Seconds)
> *"Judges, voice clone scams and deepfake audio fraud are rapidly exploding across banking, enterprise authentication, and public media. Traditional audio security cannot distinguish synthetic AI voices from genuine human speech. Presenting **VoxShield** — an AI-powered voice anti-spoofing and deepfake detection engine."*

### 2. Scenario 1: Authentic Voice Sample (SAFE)
1. **Action**: Click **"Load Genuine Voice Sample"** or record a live 3-second sentence via microphone.
2. **Visual**: The interactive waveform animates in green.
3. **Result**:
   - Status Pill: `SAFE` (Green)
   - Synthetic Score: `0.08` (8%)
   - Replay Score: `0.05` (5%)
   - Risk Meter: Low Risk Gauge
   - Explanation: *"Natural phase dynamics and clean harmonic spectrum detected."*

### 3. Scenario 2: Deepfake / Synthetic AI Voice (HIGH RISK)
1. **Action**: Click **"Load AI Voice Clone Sample"** (e.g. ElevenLabs cloned voice).
2. **Visual**: Waveform flags anomalous high frequencies in red.
3. **Result**:
   - Status Pill: `HIGH_RISK` (Red Alert)
   - Synthetic Score: `0.94` (94%)
   - Replay Score: `0.32` (32%)
   - Risk Meter: Critical Warning Meter
   - Explanation: *"Synthetic voice characteristics detected (Phase incoherence, unnatural spectral continuity)."*

### 4. Scenario 3: Audio Replay Attack (SUSPICIOUS / HIGH RISK)
1. **Action**: Upload an audio file recorded via a smartphone playing near the microphone.
2. **Result**:
   - Status Pill: `SUSPICIOUS` or `HIGH_RISK`
   - Replay Score: `0.78` (78%)
   - Explanation: *"Replay attack characteristics detected (Sub-band impulse response artifacts & room echo)."*

### 5. Technical Highlights & Summary (30 Seconds)
- Dual-layer neural classifier + DSP reverberation analyzer.
- Dynamic threat risk score engine.
- Enterprise-ready API stack (FastAPI + React).
