# VoxShield System Architecture Document

## System Overview

VoxShield is an AI-powered voice security platform designed to detect voice clones, synthetic speech, and acoustic replay attacks. The system employs a multi-stage defense-in-depth model combining deep learning anti-spoofing classifiers, digital signal processing (DSP) spectral analysis, and a dynamic risk calculation engine.

---

## High-Level Architecture Diagram

```
+-------------------------------------------------------------------------+
|                              CLIENT LAYER                               |
|                                                                         |
|  +---------------------+      +---------------------+                   |
|  | Microphone Live Rec |      | Audio File Uploader |                   |
|  +----------+----------+      +----------+----------+                   |
|             |                            |                              |
|             +--------------+-------------+                              |
|                            |                                            |
|                            v                                            |
|                +-----------------------+                                |
|                | React Dashboard (Vite)|                                |
|                | + Waveform Visualizer |                                |
|                | + Risk Meter & Alerts |                                |
|                +-----------+-----------+                                |
+----------------------------|--------------------------------------------+
                             | HTTPS / WSS
                             v
+-------------------------------------------------------------------------+
|                             BACKEND LAYER                               |
|                                                                         |
|                +-----------------------+                                |
|                | FastAPI Security Gateway|                               |
|                +-----------+-----------+                                |
|                            |                                            |
|             +--------------+--------------+                             |
|             |                             |                             |
|             v                             v                             |
|  +---------------------+       +--------------------+                   |
|  | Audio Processing    |       | Streaming Handler  |                   |
|  | & Normalization     |       | (WebSocket)        |                   |
|  +----------+----------+       +--------------------+                   |
|             |                                                           |
|             v                                                           |
|  +--------------------------------------------------+                   |
|  | FEATURE EXTRACTION (LFCC / MFCC / Spectrogram)   |                   |
|  +--------------------------+-----------------------+                   |
|                             |                                           |
|             +---------------+---------------+                           |
|             |                               |                           |
|             v                               v                           |
|  +--------------------+          +--------------------+                 |
|  | PyTorch Anti-Spoof |          | Replay DSP Analyzer|                 |
|  | Synthetic Classifier|          | Reverberation & SNR|                 |
|  +----------+---------+          +----------+---------+                 |
|             |                               |                           |
|             +---------------+---------------+                           |
|             | P(synthetic)  | P(replay)                                 |
|             v               v                                           |
|  +--------------------------------------------------+                   |
|  | RISK EVALUATION ENGINE (Heuristic & Weighting)   |                   |
|  +--------------------------+-----------------------+                   |
|                             |                                           |
|                             v                                           |
|  +--------------------------------------------------+                   |
|  | JSON Security Audit Report (Status, Scores, Logs)|                   |
|  +--------------------------------------------------+                   |
+-------------------------------------------------------------------------+
```

---

## Data Pipeline Stages

### Stage 1: Audio Ingestion & Normalization
- **Formats Accepted**: WAV, MP3, FLAC, M4A, OGG
- **Preprocessing Pipeline**:
  - Convert multi-channel input to mono 16kHz PCM.
  - Trim silence below -40dBFS threshold.
  - Peak normalization to -1.0 dBFS.

### Stage 2: Feature Extraction
- **Spectral Analysis**: Linear Frequency Cepstral Coefficients (LFCC) & Mel-Frequency Cepstral Coefficients (MFCC).
- **Time-Frequency Representations**: Constant-Q Transform (CQT) and Short-Time Fourier Transform (STFT) spectrograms.

### Stage 3: AI Anti-Spoofing Model
- **Model Target**: Predicts probability `P(synthetic)` of speech generated by neural TTS or voice cloning algorithms.
- **Model Architecture**: Deep Residual Neural Network (ResNet/RawNet) trained on acoustic phase anomalies.

### Stage 4: Replay & DSP Detection
- **Target**: Detects physical playback artifacts `P(replay)`.
- **Acoustic Markers**:
  - High-frequency roll-off (transducer frequency response limit).
  - Room impulse response reverberation patterns.
  - Secondary background white noise profile.

### Stage 5: Risk Engine Scoring
- Formula:
  $$\text{Risk Score} = 0.6 \times P(\text{synthetic}) + 0.4 \times P(\text{replay})$$
- Classification Thresholds:
  - $\text{Risk Score} < 0.35 \implies \mathbf{SAFE}$
  - $0.35 \le \text{Risk Score} < 0.70 \implies \mathbf{SUSPICIOUS}$
  - $\text{Risk Score} \ge 0.70 \implies \mathbf{HIGH\_RISK}$
