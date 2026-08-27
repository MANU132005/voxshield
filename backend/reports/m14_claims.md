# VoxShield M14 — Scientific Claims Report

## 1. Verified Claims (SAFE TO CLAIM)
- VoxShield implements an end-to-end multi-modal voice anti-spoofing and acoustic replay detection backend.
- VoxShield features 6-stage 16kHz audio normalization, 80-channel Log-Mel & 20-channel LFCC extraction, PyTorch 2D CNN inference, and Single-STFT DSP replay analysis.
- VoxShield includes automated ASVspoof-compatible dataset auditing, preflight validation, and leakage detection infrastructure.
- VoxShield includes a 6-layer multi-signal risk engine with defensive input clamping and structured evidence generation.
- VoxShield achieves mean end-to-end execution latency of ~40.7ms on modern multi-core CPUs.

## 2. Blocked Claims (NOT SAFE TO CLAIM)
- VoxShield achieves 100% / 99% accuracy on real-world voice deepfakes (Model baseline was trained on synthetic DSP demo signals).
- VoxShield is benchmarked on the official ASVspoof 2019 LA evaluation dataset (Official 15.2 GB FLAC dataset is missing locally).
- VoxShield has a scientifically calibrated Equal Error Rate (EER) on physical voice clones.
