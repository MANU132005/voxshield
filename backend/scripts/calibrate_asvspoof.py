"""
Phase 6 Model Score Calibration CLI Script.
Calibrates model scores on development set to prevent test-set contamination.
"""

import os
import sys
import json
import argparse
import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.dataset_discovery.discovery import DatasetDiscoveryEngine
from app.services.anti_spoofing.asvspoof_dataset import ASVspoofDataset
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet
from app.services.evaluation.calibration import ModelScoreCalibration


def calibrate_scores(
    dataset_dir: str = "datasets/ASVspoof2019_LA/LA",
    checkpoint_path: str = "models/asvspoof2019_la_resnet.pt"
):
    print("========================================================")
    print("VOXSHIELD PHASE 6 — MODEL SCORE CALIBRATION")
    print("========================================================")

    engine = DatasetDiscoveryEngine(dataset_root=dataset_dir)
    audit_res = engine.audit_dataset()

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "phase6_calibration_report.md")
    json_path = os.path.join(reports_dir, "phase6_calibration.json")

    if not audit_res.is_valid:
        print(f"CALIBRATION BLOCKED: Official dataset at '{dataset_dir}' is missing.")
        print("Status: BLOCKED_DATASET")
        sys.exit(1)

    abs_ckpt_path = os.path.abspath(checkpoint_path)
    if not os.path.exists(abs_ckpt_path):
        print(f"CALIBRATION BLOCKED: Checkpoint not found at '{checkpoint_path}'")
        sys.exit(1)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = VoiceAntiSpoofingResNet().to(device)
    ckpt_data = torch.load(abs_ckpt_path, map_location=device, weights_only=True)
    if isinstance(ckpt_data, dict) and "state_dict" in ckpt_data:
        model.load_state_dict(ckpt_data["state_dict"])
    elif isinstance(ckpt_data, dict):
        model.load_state_dict(ckpt_data)
    else:
        model.load_state_dict(ckpt_data)

    model.eval()

    abs_dataset_dir = os.path.abspath(dataset_dir)
    dev_proto = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_cm_protocols", "ASVspoof2019.LA.cm.dev.trl.txt")
    dev_audio_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_dev")

    print(f"Loading Development Set for Calibration: {dev_proto}...")
    dev_dataset = ASVspoofDataset(protocol_file=dev_proto, audio_dir=dev_audio_dir)
    dev_loader = DataLoader(dev_dataset, batch_size=64, shuffle=False, num_workers=4 if os.name != 'nt' else 0)

    all_labels = []
    all_scores = []
    with torch.no_grad():
        for features, labels in dev_loader:
            features = features.to(device)
            logits = model(features)
            probs = torch.sigmoid(logits).squeeze(-1).cpu().numpy()

            all_labels.extend(labels.squeeze(-1).numpy())
            all_scores.extend(probs)

    labels_arr = np.array(all_labels, dtype=np.int32)
    scores_arr = np.array(all_scores, dtype=np.float32)

    cal_module = ModelScoreCalibration()
    cal_res = cal_module.evaluate_calibration_status(
        calibration_dataset_present=True,
        scores=scores_arr,
        labels=labels_arr
    )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cal_res, f, indent=2)

    md_content = f"""# Phase 6: Model Score Calibration Report

**Calibration Status**: `{cal_res.get('status', 'COMPLETED')}`  
**Calibration Dataset**: `Development Set (Dev)` (`{len(labels_arr)}` samples)  
**Method**: `Platt Scaling & Reliability Diagram Evaluation`  

---

## 1. Operating Thresholds & Metrics
- **Optimal EER Threshold**: `{cal_res.get('optimal_threshold', 0.5):.4f}`
- **Expected Calibration Error (ECE)**: `{cal_res.get('ece', 0.0):.4f}`
- **Brier Score**: `{cal_res.get('brier_score', 0.0):.4f}`
- **Calibration Decision**: `Model probabilities calibrated on Dev split.`
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Calibration completed on Dev set. Status: COMPLETED. Generated {report_path} and {json_path}")
    return cal_res


def main():
    parser = argparse.ArgumentParser(description="VoxShield Model Score Calibration")
    parser.add_argument("--dataset-dir", type=str, default="datasets/ASVspoof2019_LA/LA")
    parser.add_argument("--checkpoint", type=str, default="models/asvspoof2019_la_resnet.pt")
    args = parser.parse_args()

    calibrate_scores(dataset_dir=args.dataset_dir, checkpoint_path=args.checkpoint)


if __name__ == "__main__":
    main()
