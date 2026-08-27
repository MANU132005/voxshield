# VoxShield M14 — Checkpoint Audit Report

**Audit Status**: PASS — CHECKPOINT INTEGRITY VERIFIED  
**Baseline Checkpoint**: C:\Users\Lenovo\voxshield\backend\models\anti_spoofing_resnet.pt  

---

## 1. Baseline Checkpoint Verification
- **File Found**: True
- **SHA-256 Hash**: decd20c8d5ec9aff079d613b268d0857ab32fc655006ac11d485a08b613161a3
- **File Size**: 4.7 MB
- **NaN / Inf Weight Inspection**: PASS
- **BatchNorm Tracker (
um_batches_tracked)**: 72
- **Provenance Classification**: DEMO_DSP_SYNTHETIC_DATASET
- **Provenance Note**: Model was trained for 8 epochs on DSP-generated synthetic signals (72 batches). Has zero real-world ASVspoof capability.

---

## 2. Real ASVspoof Model Checkpoint Status
- **Target Path**: ackend/models/anti_spoofing_asvspoof2019_la.pt
- **Status**: NOT CREATED — REAL TRAINING BLOCKED DUE TO MISSING DATASET
