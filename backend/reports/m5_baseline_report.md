# Milestone 5 Anti-Spoofing Model Baseline Evaluation Report

**Evaluation Date**: 2026-08-24  
**Evaluated Checkpoint**: [`backend/models/anti_spoofing_resnet.pt`](file:///c:/Users/Lenovo/voxshield/backend/models/anti_spoofing_resnet.pt)  
**Model Architecture**: `VoiceAntiSpoofingResNet` (ResNet-18 2D Convolutional Neural Network)  
**Model Version**: `resnet18_logmel_v1.0`  

---

## 📊 Summary of Baseline Metrics

The baseline evaluation was performed on the held-out test split of 60 synthetic DSP audio samples (29 genuine, 31 spoofed).

| Metric | Score | Note |
| :--- | :--- | :--- |
| **Accuracy** | **100.00%** | All 60 test samples correctly classified |
| **Precision** | **1.0000** | Zero false alarms ($FP = 0$) |
| **Recall (Detection Rate)** | **1.0000** | Zero missed deepfakes ($FN = 0$) |
| **F1-Score** | **1.0000** | Harmonic mean of Precision and Recall |
| **ROC-AUC** | **1.0000** | Perfect separation across decision thresholds |
| **Equal Error Rate (EER)** | **0.00%** | Threshold where $FAR = FRR$ |

---

## 🔍 Confusion Matrix

| | Predicted Genuine | Predicted Spoof | Total |
| :--- | :---: | :---: | :---: |
| **Actual Genuine** | **TN = 29** | FP = 0 | 29 |
| **Actual Spoof** | FN = 0 | **TP = 31** | 31 |
| **Total** | 29 | 31 | **60** |

---

## ⚠️ Scientific Audit Note

> [!CAUTION]
> **Data Origin Limitation**: The test set samples were generated in-memory via mathematical DSP signal equations (harmonic sinusoids vs. square-wave vocoder phase artifacts). While this demonstrates that the end-to-end backend pipeline (Audio Processing $\rightarrow$ Feature Extraction $\rightarrow$ PyTorch Forward Pass) is fully functional and numerically deterministic, **these metrics do NOT reflect real-world generalization to human speech or commercial AI voice cloners (e.g. ElevenLabs, VALL-E)**. Independent validation on public benchmarks (ASVspoof 2019 LA) is required before presenting accuracy metrics to external stakeholders.
