# VoxShield M9 — ASVspoof 2019 LA Dataset Audit Report

**Dataset Status**: `BLOCKED — REAL ASVSPOOF DATASET NOT PRESENT`  
**Training Status**: `NOT_EXECUTED`  
**Inspected Root Directory**: `C:\Users\Lenovo\voxshield\backend\non_existent_asvspoof_dataset`  

---

## 1. Executive Summary
The official ASVspoof 2019 Logical Access dataset archive (`LA.zip` / FLAC audio files / `ASVspoof2019.LA.cm.*.txt`) is **NOT** present on local disk. Per VoxShield quality rules, zero sample counts or audio statistics were fabricated.

---

## 2. Dataset Discovery
- **Dataset Found**: `False`
- **Candidate Paths Searched**:
  - `C:\Users\Lenovo\voxshield\backend\non_existent_asvspoof_dataset`
  - `C:\Users\Lenovo\voxshield\backend\datasets\ASVspoof2019_LA`
- **Selected Root**: `None`

---

## 3. Partition Statistics

| Partition | Protocol Entries | Audio Files Found | Bona-fide | Spoof | Missing Files | Corrupt Files |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Train** | 0 | 0 | 0 | 0 | N/A | N/A |
| **Dev** | 0 | 0 | 0 | 0 | N/A | N/A |
| **Eval** | 0 | 0 | 0 | 0 | N/A | N/A |

---

## 4. Audio Integrity & Leakage Analysis
- **Sample Rate Distribution**: `N/A`
- **Channel Distribution**: `N/A`
- **Utterance Overlap Across Splits**: `N/A`
- **Speaker Overlap Across Splits**: `N/A`
- **Path Traversal Security**: `PASS`

---

## 5. Required Action
Download `LA.zip` from Edinburgh DataShare (`https://datashare.ed.ac.uk/handle/10283/3336`) and extract into `C:\Users\Lenovo\voxshield\backend\non_existent_asvspoof_dataset` before proceeding to M10 model training.
