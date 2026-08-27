# Milestone 15: Forensic Engine Architecture Specification

**Module**: VoxShield Backend AI & Forensics Architecture  
**Date**: 2026-08-25  

---

## 1. Multi-Layer Pipeline Architecture

```text
POST /api/v1/analyze (Audio Upload)
       │
       ▼
AudioProcessor (16kHz Mono, Peak Norm -1.0 dBFS)
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
FeatureExtractor (Log-Mel & LFCC)   Single-STFT Replay DSP Engine
       │                                 │
       ▼                                 ▼
VoiceAntiSpoofingResNet (2D CNN)     ReplayDetector (Spectral Flux, Centroid, Rolloff)
       │                                 │
       └────────────────┬────────────────┘
                        │
                        ▼
             ForensicEngine Aggregator
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
Spectral Forensics Temporal Forensics Signal Integrity
(Flatness, Entropy) (ZCR, Envelope)  (Clipping, DC, Crest)
       └────────────────┬────────────────┘
                        │
                        ▼
            Signal Consistency Engine
                        │
                        ▼
            Uncertainty Engine (Confidence Indicator)
                        │
                        ▼
            Attack Taxonomy Classifier
                        │
                        ▼
            AnalysisResponse (JSON Output)
```
