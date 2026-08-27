# Phase 6: ASVspoof 2019 LA Dataset Discovery & Audit Report

**Dataset Name**: `ASVspoof 2019 Logical Access`  
**Dataset Root**: `C:\Users\Lenovo\voxshield\backend\datasets\ASVspoof2019_LA\LA`  
**Status**: `INTEGRITY_VERIFIED`  
**Is Valid Physical Dataset**: `True`  
**Total Audio Files**: `122299`  
**Total Protocol Entries**: `121461`  
**Leakage Detected**: `False`  

---

## 1. Scientific Disclosures & Prerequisite Requirements
> [!IMPORTANT]
> - Official ASVspoof 2019 LA dataset directory `backend/datasets/ASVspoof2019_LA/LA` physical audit rule enforced.
> - If local dataset is missing: **`STATUS = BLOCKED_DATASET`**. Real training and benchmark certification remain strictly **`BLOCKED`**.

---

## 2. Split Audit Summary

| Split | Audio Files | Protocol Lines | Speakers | Bonafide | Spoof | Missing Files |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Train | `25380` | `25380` | `20` | `2580` | `22800` | `0` |
| Dev | `24986` | `24844` | `20` | `2548` | `22296` | `0` |
| Eval | `71933` | `71237` | `67` | `7355` | `63882` | `0` |
