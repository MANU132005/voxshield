"""
Phase 6 ASVspoof 2019 LA Dataset Audit CLI Script.

Audits dataset root, FLAC audio files, protocol files, cross-split speaker/hash leakage,
and generates phase6_dataset_audit.md and phase6_dataset_status.json.
"""

import os
import sys
import json
from dataclasses import asdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.dataset_discovery.discovery import DatasetDiscoveryEngine


def main():
    print("========================================================")
    print("VOXSHIELD PHASE 6 — DATASET ACQUISITION & INTEGRITY AUDIT")
    print("========================================================")

    engine = DatasetDiscoveryEngine(dataset_root="datasets/ASVspoof2019_LA/LA")
    audit_res = engine.audit_dataset()

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)

    json_path = os.path.join(reports_dir, "phase6_dataset_status.json")
    md_path = os.path.join(reports_dir, "phase6_dataset_audit.md")

    audit_dict = asdict(audit_res)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(audit_dict, f, indent=2)

    md_content = f"""# Phase 6: ASVspoof 2019 LA Dataset Discovery & Audit Report

**Dataset Name**: `{audit_res.dataset_name}`  
**Dataset Root**: `{audit_res.dataset_root}`  
**Status**: `{audit_res.status}`  
**Is Valid Physical Dataset**: `{audit_res.is_valid}`  
**Total Audio Files**: `{audit_res.total_audio_files}`  
**Total Protocol Entries**: `{audit_res.total_protocol_entries}`  
**Leakage Detected**: `{audit_res.leakage_detected}`  

---

## 1. Scientific Disclosures & Prerequisite Requirements
> [!IMPORTANT]
> - Official ASVspoof 2019 LA dataset directory `backend/datasets/ASVspoof2019_LA/LA` physical audit rule enforced.
> - If local dataset is missing: **`STATUS = BLOCKED_DATASET`**. Real training and benchmark certification remain strictly **`BLOCKED`**.

---

## 2. Split Audit Summary
"""

    if audit_res.is_valid:
        md_content += f"""
| Split | Audio Files | Protocol Lines | Speakers | Bonafide | Spoof | Missing Files |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Train | `{audit_res.train_split.audio_file_count}` | `{audit_res.train_split.protocol_line_count}` | `{audit_res.train_split.speakers_count}` | `{audit_res.train_split.bonafide_count}` | `{audit_res.train_split.spoof_count}` | `{len(audit_res.train_split.missing_audio_files)}` |
| Dev | `{audit_res.dev_split.audio_file_count}` | `{audit_res.dev_split.protocol_line_count}` | `{audit_res.dev_split.speakers_count}` | `{audit_res.dev_split.bonafide_count}` | `{audit_res.dev_split.spoof_count}` | `{len(audit_res.dev_split.missing_audio_files)}` |
| Eval | `{audit_res.eval_split.audio_file_count}` | `{audit_res.eval_split.protocol_line_count}` | `{audit_res.eval_split.speakers_count}` | `{audit_res.eval_split.bonafide_count}` | `{audit_res.eval_split.spoof_count}` | `{len(audit_res.eval_split.missing_audio_files)}` |
"""
    else:
        md_content += "\n> [!WARNING]\n> Dataset files are missing on local disk. Extract official ASVspoof 2019 LA FLAC dataset into `backend/datasets/ASVspoof2019_LA/LA` to unblock audit verification.\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Dataset Audit Status: {audit_res.status}")
    print(f"Is Physical Dataset Valid: {audit_res.is_valid}")
    print(f"Saved reports to: {md_path} and {json_path}")


if __name__ == "__main__":
    main()
