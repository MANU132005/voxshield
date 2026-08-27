# VoxShield M14 — Dataset Preflight & Integrity Audit Report

**Audit Status**: BLOCKED_DATASET  
**Inspected Root Directory**: C:\Users\Lenovo\voxshield\backend\datasets\ASVspoof2019_LA\LA  

---

## 1. Preflight Summary
- **Dataset Found**: False
- **Train Protocol**: False
- **Dev Protocol**: False
- **Eval Protocol**: False
- **Hard Block Reason**: Official ASVspoof 2019 Logical Access (LA) 15.2 GB FLAC dataset archive (LA.zip) is missing on local disk.

---

## 2. Hard Block Decision
Per VoxShield M14 Absolute Rules:
- Real ASVspoof model training and held-out evaluation are **BLOCKED**.
- Zero training metrics or accuracy numbers were fabricated.
- Baseline checkpoint ackend/models/anti_spoofing_resnet.pt remains preserved with DEMO_DSP_SYNTHETIC_DATASET provenance.
