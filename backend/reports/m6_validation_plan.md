# Milestone 6: Independent Model Validation Plan

This document outlines the protocol for validating VoxShield's AI anti-spoofing model against genuinely unseen real-world human speech and deepfake voice clones.

---

## 🎯 Validation Objectives

To ensure scientific defensibility and eliminate dataset leakage, the anti-spoofing model must be evaluated against three distinct audio categories that were **never present** during training:

1. **Unseen Genuine Human Speech**: Real multi-speaker human recordings across diverse age groups, accents, genders, and acoustic environments (e.g., LibriSpeech, VCTK).
2. **Unseen Neural TTS Speech**: Speech synthesized by modern Text-to-Speech models (e.g., Tacotron 2, FastSpeech 2, VITS, Bark).
3. **Unseen Voice-Converted / Cloned Speech**: Speech produced by neural voice cloning algorithms (e.g., ElevenLabs, OpenVoice, DiffVC, StarGAN-Voice).

---

## 🛡️ Leakage-Safe Evaluation Protocol

### 1. Speaker Disjointness
- No speaker ID present in the validation/test set will appear in any training set split.

### 2. Vocoder & Model Disjointness
- Evaluation will test zero-day attack algorithms ($A07-A19$ in ASVspoof 2019 LA) that use unseen neural vocoders and synthesis architectures.

### 3. Metric Reporting Requirements
Validation runs must record:
- **Equal Error Rate (EER)**
- **ROC-AUC**
- **Precision, Recall, F1-Score**
- **Confusion Matrix (TP, FP, TN, FN)**

---

## 📁 Validation Dataset Source

- **Dataset**: ASVspoof 2019 LA Evaluation Split (`ASVspoof2019_LA_eval`)
- **Size**: 71,237 audio files (7,355 genuine, 63,882 spoofed across 13 unseen attack algorithms).
- **Execution**: Run via `scripts/evaluate_asvspoof.py` without modifying model weights.
