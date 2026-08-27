# Phase 6: Real ASVspoof 2019 LA Evaluation Report

**Evaluation Status**: `COMPLETED`  
**Dataset Path**: `C:\Users\Lenovo\voxshield\backend\datasets\ASVspoof2019_LA\LA`  
**Evaluated Checkpoint**: `C:\Users\Lenovo\voxshield\backend\models\asvspoof2019_la_smoketest.pt`  
**Checkpoint SHA-256**: `c67d75337eac3a5935100ca8cc513d63d7cb06f02cfce56d4a7ea98360469289`  
**Total Samples**: `71237` (`7355` bonafide, `63882` spoof)  
**Evaluation Duration**: `4105.7s`  

---

## 1. Measured Performance Metrics
- **Equal Error Rate (EER)**: `0.5000` (50.00%) at threshold `0.0000`
- **ROC-AUC**: `0.5000`
- **Accuracy**: `0.8968` (89.68%)
- **Precision**: `0.8968`
- **Recall**: `1.0000`
- **F1 Score**: `0.9456`
- **False Acceptance Rate (FAR)**: `1.0000` (100.00%)
- **False Rejection Rate (FRR)**: `0.0000` (0.00%)

---

## 2. Confusion Matrix (at Default Operating Point 0.5)

| Metric | Count |
| :--- | :--- |
| **True Positives (Spoof Detected)** | `63882` |
| **True Negatives (Bonafide Accepted)** | `0` |
| **False Positives (Bonafide Flagged as Spoof)** | `7355` |
| **False Negatives (Spoof Passed as Bonafide)** | `0` |
