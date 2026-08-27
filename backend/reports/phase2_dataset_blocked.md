# Phase 2: Dataset Discovery & Audit Report

**Phase 2 Status**: `BLOCKED_DATASET`  
**Dataset Gate Status**: `DATASET_MISSING`  
**Real Training Status**: `REAL_TRAINING_NOT_EXECUTED`  
**Real Metrics Status**: `REAL_METRICS_N/A`  
**Benchmark Certification**: `BENCHMARK_CERTIFICATION_BLOCKED`  

---

## 1. Dataset Discovery Result
Empirical inspection confirmed that the official ASVspoof 2019 Logical Access dataset directory (`backend/datasets/ASVspoof2019_LA/LA`) is **NOT PRESENT** on local disk.

Per absolute scientific rules:
- Real model training was **HALTED**.
- Zero fake metrics (Accuracy, EER, ROC-AUC, Precision, Recall, F1) were generated.
- Synthetic/demo audio was **NOT** substituted for ASVspoof evaluation.
- Baseline synthetic checkpoint (`backend/models/anti_spoofing_resnet.pt`) remains preserved intact.

---

## 2. Required Official Dataset Files
To enable real model training and benchmark certification, download the official 15.2 GB ASVspoof 2019 LA FLAC archive (`LA.zip`) from Edinburgh DataShare:
`https://datashare.ed.ac.uk/handle/10283/3336`

Extract the contents into:
`backend/datasets/ASVspoof2019_LA/LA/`

Required protocol & audio files:
- `ASVspoof2019.LA.cm.train.trn.txt` (25,380 records)
- `ASVspoof2019.LA.cm.dev.trl.txt` (24,844 records)
- `ASVspoof2019.LA.cm.eval.trl.txt` (71,237 records)
- `ASVspoof2019_LA_train/flac/*.flac`
- `ASVspoof2019_LA_dev/flac/*.flac`
- `ASVspoof2019_LA_eval/flac/*.flac`
