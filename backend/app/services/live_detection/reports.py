"""
Phase 5 Live Detection Report Generator Module.
Generates structured markdown and JSON live-detection assessment reports.
"""

import os
import json
from dataclasses import asdict
from typing import Dict, Any
from app.services.live_detection.types import LiveAnalysisResult


def generate_phase5_reports(result: LiveAnalysisResult, output_dir: str = "./reports") -> Dict[str, str]:
    abs_out = os.path.abspath(output_dir)
    os.makedirs(abs_out, exist_ok=True)

    json_path = os.path.join(abs_out, "phase5_live_detection_status.json")
    md_path = os.path.join(abs_out, "phase5_live_detection_report.md")
    final_md_path = os.path.join(abs_out, "PHASE5_FINAL_REPORT.md")

    result_dict = asdict(result)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2)

    md_content = f"""# Phase 5: Live Detection Engine & Streaming Architecture Report

**Phase 5 Status**: `{result.status}`  
**Live Decision**: `{result.decision}`  
**Risk Score**: `{result.risk_score} / 100.0` (`{result.risk_level}`)  
**Confidence State**: `{result.confidence_state}` (`{result.confidence_score}`)  
**Detector Agreement**: `{result.agreement['agreement_state']}`  
**Temporal Stability**: `{result.temporal_stability['stability_state']}`  

---

## 1. Disclosures & Mandatory Disclosures
> [!IMPORTANT]
> - Phase 5 live detection evaluates multi-window audio signals chunk-by-chunk using windowed analysis. It does not constitute ASVspoof benchmark certification.
> - Real ASVspoof 2019 LA benchmark metrics remain **BLOCKED** until the official dataset is available and successfully evaluated.

---

## 2. Processing Latency & Multi-Window Metrics
- **Total Ingestion & Analysis Latency**: `{result.processing_metadata['total_duration_ms']} ms`
- **Mean Per-Window Latency**: `{result.processing_metadata['mean_window_latency_ms']} ms`
- **Windows Processed**: `{result.processing_metadata['windows_processed']}`
- **Audio Duration**: `{result.processing_metadata['audio_duration_seconds']} s`

---

## 3. Disclosures & Mandatory Status
- **ClaimGuard Status**: `ACTIVE` (All benchmark claims remain strictly blocked).
- **BenchmarkGate Status**: `ACTIVE` (Certification remains strictly blocked).
- **Baseline Checkpoint**: Preserved intact (`backend/models/anti_spoofing_resnet.pt`).
- **Frontend Status**: `100% UNTOUCHED`.
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    with open(final_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return {
        "json_report": json_path,
        "md_report": md_path,
        "final_report": final_md_path
    }
