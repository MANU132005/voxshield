# Milestone 13: Model Integrity & Provenance Audit Report

**Audit Date**: 2026-08-25  
**Target Checkpoint**: C:\Users\Lenovo\voxshield\backend\models\anti_spoofing_resnet.pt  

---

## 1. Checkpoint Verification Summary
- **Checkpoint Found**: True
- **SHA-256 Hash**: decd20c8d5ec9aff079d613b268d0857ab32fc655006ac11d485a08b613161a3
- **File Size**: 4.7 MB (4926385 bytes)
- **NaN / Inf Weight Corruption**: False
- **BatchNorm Tracker (
um_batches_tracked)**: 72

---

## 2. Provenance Audit
- **Provenances Status**: DEMO_DSP_SYNTHETIC_DATASET
- **Provenance Note**: Model was trained for 8 epochs on DSP-generated synthetic signals (72 batches). Has zero real-world ASVspoof capability.
- **Status**: PASS — CHECKPOINT INTEGRITY VERIFIED
