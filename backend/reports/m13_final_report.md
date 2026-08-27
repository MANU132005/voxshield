# VoxShield M13 Final Report — Real-World Evaluation, Model Integrity & Scientific Validation

**Date**: 2026-08-25  
**Evaluation Status**: `BLOCKED_DATASET — REAL ASVSPOOF DATASET NOT PRESENT`  
**Model Provenance**: `DEMO_DSP_SYNTHETIC_DATASET`  

---

## 1. Executive Summary

Milestone 13 establishes the scientific integrity, model provenance audit, and leakage-safe real-world evaluation infrastructure for VoxShield. 

Per VoxShield's strict scientific rules:
1. Zero accuracy, precision, recall, F1, ROC-AUC, or EER metrics were fabricated on fake or demo audio.
2. The model evaluation status is reported honestly as `BLOCKED_DATASET`.
3. Baseline checkpoint `anti_spoofing_resnet.pt` is audited and documented as trained on DSP synthetic demo signals (`num_batches_tracked = 72`).
4. The `ClaimGuard` module was deployed to enforce scientific boundary validation across APIs and reports.

---

## 2. Model Integrity & Checkpoint Audit

- **Checkpoint File**: `backend/models/anti_spoofing_resnet.pt`
- **File Size**: `4.92 MB (5,158,541 bytes)`
- **SHA-256 Hash**: `c570b209e530fb15e5138139cdbeeeff51eeae99580b0c79f976a16174a7bca0`
- **NaN / Inf Weight Inspection**: `PASS` (Zero NaN or Inf parameters detected)
- **BatchNorm Tracker (`num_batches_tracked`)**: `72`
- **Provenance Conclusion**: `DEMO_DSP_SYNTHETIC_DATASET` (Requires real ASVspoof dataset uncompression for benchmark training).

---

## 3. ASVspoof 2019 Dataset Discovery Result

- **Dataset Root Inspected**: `c:\Users\Lenovo\voxshield\backend\datasets\ASVspoof2019_LA\LA`
- **Dataset Status**: `DATASET_MISSING`
- **Missing Files**: Official 15.2 GB FLAC audio dataset archive (`LA.zip`) and protocol text files (`ASVspoof2019.LA.cm.eval.trl.txt`).

---

## 4. SIH Claim Safety Guidelines

### SAFE TO CLAIM:
- *"VoxShield implements an end-to-end multi-modal voice anti-spoofing and acoustic replay detection backend."*
- *"VoxShield features 6-stage 16kHz audio normalization, 80-channel Log-Mel & 20-channel LFCC extraction, PyTorch 2D CNN inference, and Single-STFT DSP replay analysis."*
- *"VoxShield includes automated ASVspoof-compatible dataset auditing and leakage detection infrastructure."*
- *"VoxShield includes a 6-layer multi-signal risk engine with defensive input clamping and structured evidence generation."*

### NOT SAFE TO CLAIM:
- *"VoxShield achieves 100% / 99% accuracy on real-world voice deepfakes (Model was trained on synthetic DSP demo signals)."*
- *"VoxShield is benchmarked on the official ASVspoof 2019 LA evaluation dataset (Official 15.2 GB FLAC dataset is missing locally)."*
- *"VoxShield has a scientifically calibrated Equal Error Rate (EER) on physical voice clones."*

---

## 5. Final Status
```text
BLOCKED_DATASET — REAL ASVSPOOF DATASET NOT PRESENT
```
