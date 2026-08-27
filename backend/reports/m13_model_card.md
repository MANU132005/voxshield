# VoxShield Model Card — VoiceAntiSpoofingResNet

**Model Name**: `VoiceAntiSpoofingResNet`  
**Model Version**: `1.0.0-demo`  
**Architecture**: 2D Residual Convolutional Neural Network (3 Residual Blocks, 32 $\rightarrow$ 64 $\rightarrow$ 128 $\rightarrow$ 256 channels)  
**Date**: 2026-08-25  

---

## 1. Model Overview & Input Specifications

- **Input Representation**: 80-channel Log-Mel Spectrogram tensor `(batch_size, 1, 80, 300)` float32.
- **Audio Preprocessing**: Mono 16,000 Hz, polyphase resampled, peak normalized to -1.0 dBFS, Z-score channel normalized.
- **Output**: Single scalar float `synthetic_score` $[0.0 - 1.0]$ representing synthetic voice likelihood.

---

## 2. Checkpoint Provenance & Training Data Disclosures

> [!WARNING]
> **Training Data Disclosure**: Baseline checkpoint `backend/models/anti_spoofing_resnet.pt` was trained for 8 epochs on DSP-generated synthetic signals (`num_batches_tracked = 72`). **It has ZERO real-world ASVspoof detection capability.** Real ASVspoof 2019 training will occur in Milestone 14 upon uncompressing the official dataset.

- **Checkpoint SHA-256**: `c570b209e530fb15e5138139cdbeeeff51eeae99580b0c79f976a16174a7bca0`
- **File Size**: `4.92 MB (5,158,541 bytes)`
- **Real-World ASVspoof Verified Status**: `NOT_VERIFIED`

---

## 3. Intended & Non-Intended Uses

### Intended Uses:
- Multi-modal voice anti-spoofing research and engineering validation backend.
- Integration into multi-factor authentication risk scoring pipelines (in combination with biometrics and replay DSP).

### Non-Intended Uses:
- Standalone automated biometric authentication without human-in-the-loop or secondary factors.
- Standalone legal or forensic voice deepfake determination without expert acoustic review.

---

## 4. Honest Limitations & Security Considerations
- Current baseline checkpoint must be re-trained on official ASVspoof 2019 LA FLAC dataset before deploying to production environments.
