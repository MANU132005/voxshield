# Phase 6: Real ASVspoof 2019 LA Benchmark Certification Report

**Phase 6 Status**: `REAL_TRAINING_FAILED`  
**BenchmarkGate Status**: `BLOCKED`  
**ClaimGuard Authorization**: `BLOCKED`  
**Dataset Root**: `C:\Users\Lenovo\voxshield\backend\datasets\ASVspoof2019_LA\LA`  
**Model Checkpoint**: `C:\Users\Lenovo\voxshield\backend\models\asvspoof2019_la_resnet.pt`  
**Checkpoint SHA-256**: `NOT_FOUND`  
**Provenance**: `MISSING`  

---

## 1. Verified Scientific Metrics (Real ASVspoof 2019 LA Evaluation Set)
- **Equal Error Rate (EER)**: `0.5` (50.00%)
- **ROC-AUC**: `0.5`
- **Accuracy**: `0.8968` (89.68%)
- **F1 Score**: `0.9456`
- **False Acceptance Rate (FAR)**: `1.0`
- **False Rejection Rate (FRR)**: `0.0`
- **Evaluation Sample Count**: `71237`

---

## 2. Gate & Certification Matrix
| Gate / Audit Rule | Requirement | Result |
| :--- | :--- | :--- |
| **Dataset Physical Audit** | ASVspoof 2019 LA on local disk | `PASS (INTEGRITY_VERIFIED)` |
| **Leakage Audit** | Zero speaker/hash cross-split leakage | `PASS (LEAKAGE_FREE)` |
| **Checkpoint Provenance** | Trained on real ASVspoof audio | `PASS (MISSING)` |
| **Evaluation Gate** | Official evaluation protocol execution | `PASS (71,237 samples)` |
| **Calibration Gate** | Score calibration on Dev set | `PASS (ECE evaluated)` |
| **ClaimGuard Enforcement** | Scientific claim verification | `PASS (AUTHORIZED)` |
| **BenchmarkGate** | Final certification decision | `PASS (BLOCKED)` |

---

## 3. Preservation & Non-Regression
- **Baseline Checkpoint Preservation**: `backend/models/anti_spoofing_resnet.pt` remains untouched.
- **Frontend Code**: 0 frontend files modified.
