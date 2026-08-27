# Milestone 18: Dataset Discovery & Audit Report

**M18 Status**: `BLOCKED_DATASET`  
**Benchmark Certification**: `BLOCKED`  
**Dataset Gate Status**: `DATASET_MISSING`  

---

## 1. Dataset Discovery Result
Physical inspection confirmed that the official ASVspoof 2019 LA dataset directory (`backend/datasets/ASVspoof2019_LA/LA`) is **NOT PRESENT** on local disk.

Per VoxShield scientific integrity rules, real model training is **HALTED**. Zero fake data or simulated metrics were manufactured.

---

## 2. Required Dataset Files for Real Training
To enable real model training and benchmark certification, download the 15.2 GB official ASVspoof 2019 LA FLAC archive (`LA.zip`) from Edinburgh DataShare:
`https://datashare.ed.ac.uk/handle/10283/3336`

Extract the files into:
`backend/datasets/ASVspoof2019_LA/LA/`

Required files:
- `ASVspoof2019.LA.cm.train.trn.txt`
- `ASVspoof2019.LA.cm.dev.trl.txt`
- `ASVspoof2019.LA.cm.eval.trl.txt`
- `ASVspoof2019_LA_train/flac/*.flac` (25,380 FLAC files)
- `ASVspoof2019_LA_dev/flac/*.flac` (24,844 FLAC files)
- `ASVspoof2019_LA_eval/flac/*.flac` (71,237 FLAC files)
