# Milestone 15: Scientific Claim Safety Report

**Module**: VoxShield ClaimGuard System  
**Date**: 2026-08-25  

---

## 1. Overview & Classification System

The `ClaimGuard` module classifies all system capabilities and performance claims into 5 scientific categories:
- **`VERIFIED`**: Empirical metric measured on official dataset split.
- **`MEASURED`**: Engineering metric measured on local execution environment.
- **`INFERRED`**: Rule-based or heuristic security logic.
- **`UNVERIFIED`**: Claim lacking empirical benchmark execution.
- **`BLOCKED`**: Evaluation cannot execute due to missing dataset.

---

## 2. SIH Claim Matrix

### ✅ SAFE TO CLAIM:
- *"VoxShield combines neural, acoustic, spectral, temporal, and signal-integrity evidence into an explainable voice-security assessment."*
- *"VoxShield features 6-stage 16kHz audio normalization, 80-channel Log-Mel & 20-channel LFCC extraction, PyTorch 2D CNN inference, and Single-STFT DSP replay analysis."*
- *"VoxShield includes automated ASVspoof-compatible dataset auditing, preflight validation, and leakage detection infrastructure."*
- *"VoxShield features a multi-vector Forensic Intelligence Engine producing structured EvidenceItem graphs and attack hypothesis classifications."*
- *"VoxShield achieves mean end-to-end execution latency of ~40ms - 45ms on modern multi-core CPUs."*

### ❌ NOT SAFE TO CLAIM:
- *"VoxShield detects AI-generated voices with 100% / 99% accuracy on real-world voice clones (Model baseline was trained on synthetic DSP demo signals)."*
- *"VoxShield is benchmarked on the official ASVspoof 2019 LA evaluation dataset (Official 15.2 GB FLAC dataset is missing locally)."*
- *"VoxShield has a scientifically calibrated Equal Error Rate (EER) on physical voice clones."*
- *"VoxShield detects all AI-generated voice clones or replay attacks seamlessly."*
