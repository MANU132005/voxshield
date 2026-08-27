"""
Phase 6 Real ASVspoof Evaluation CLI Script.
Computes EER, ROC-AUC, FAR/FRR metrics on official evaluation set when dataset is present.
"""

import os
import sys
import time
import json
import argparse
import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.dataset_discovery.discovery import DatasetDiscoveryEngine
from app.services.anti_spoofing.asvspoof_dataset import ASVspoofDataset
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet
from app.services.model_integrity.auditor import audit_model_checkpoint, calculate_file_sha256
from app.services.evaluation.metric_engine import MetricEngine


def evaluate_model(
    dataset_dir: str = "datasets/ASVspoof2019_LA/LA",
    checkpoint_path: str = "models/asvspoof2019_la_resnet.pt",
    batch_size: int = 64
):
    print("========================================================")
    print("VOXSHIELD PHASE 6 — REAL ASVSPOOF EVALUATION PIPELINE")
    print("========================================================")

    engine = DatasetDiscoveryEngine(dataset_root=dataset_dir)
    audit_res = engine.audit_dataset()

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "phase6_evaluation_report.md")
    json_path = os.path.join(reports_dir, "phase6_evaluation_metrics.json")

    if not audit_res.is_valid:
        print(f"EVALUATION BLOCKED: Official dataset at '{dataset_dir}' is missing.")
        print("Status: BLOCKED_DATASET")

        md_content = f"""# Phase 6: Real ASVspoof 2019 LA Evaluation Report

**Evaluation Status**: `BLOCKED_DATASET`  
**EER**: `N/A / BLOCKED`  
**ROC-AUC**: `N/A / BLOCKED`  
**Precision / Recall / F1**: `N/A / BLOCKED`  

> [!WARNING]
> Evaluation halted per scientific integrity rules. Real-world ASVspoof evaluation metrics cannot be manufactured.
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        sys.exit(1)

    abs_ckpt_path = os.path.abspath(checkpoint_path)
    if not os.path.exists(abs_ckpt_path):
        print(f"EVALUATION BLOCKED: Checkpoint not found at '{checkpoint_path}'")
        sys.exit(1)

    # Verify Checkpoint Provenance
    ckpt_audit = audit_model_checkpoint(abs_ckpt_path)
    print(f"Checkpoint Provenance: {ckpt_audit['provenance']}")
    print(f"Checkpoint SHA-256: {ckpt_audit['sha256_hash']}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluation Compute Device: {device}")

    # Load Model
    model = VoiceAntiSpoofingResNet().to(device)
    ckpt_data = torch.load(abs_ckpt_path, map_location=device, weights_only=True)
    if isinstance(ckpt_data, dict) and "state_dict" in ckpt_data:
        model.load_state_dict(ckpt_data["state_dict"])
    elif isinstance(ckpt_data, dict):
        model.load_state_dict(ckpt_data)
    else:
        model.load_state_dict(ckpt_data)

    model.eval()

    # Evaluation Dataset
    abs_dataset_dir = os.path.abspath(dataset_dir)
    eval_proto = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_cm_protocols", "ASVspoof2019.LA.cm.eval.trl.txt")
    eval_audio_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_eval")

    print(f"Loading ASVspoof 2019 LA Evaluation Protocol: {eval_proto}...")
    eval_dataset = ASVspoofDataset(protocol_file=eval_proto, audio_dir=eval_audio_dir)
    eval_loader = DataLoader(
        eval_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4 if os.name != 'nt' else 0,
        pin_memory=(device.type == "cuda")
    )

    print(f"Evaluation samples count: {len(eval_dataset)} ({len(eval_loader)} batches)")

    all_labels = []
    all_scores = []
    t_start = time.time()

    print("Running inference over official ASVspoof evaluation dataset...")
    with torch.no_grad():
        for batch_idx, (features, labels) in enumerate(eval_loader):
            features = features.to(device)
            logits = model(features)
            probs = torch.sigmoid(logits).squeeze(-1).cpu().numpy()

            all_labels.extend(labels.squeeze(-1).numpy())
            all_scores.extend(probs)

            if (batch_idx + 1) % 200 == 0 or (batch_idx + 1) == len(eval_loader):
                print(f"Evaluated {len(all_labels)}/{len(eval_dataset)} samples...")

    eval_dur = time.time() - t_start
    print(f"Inference completed in {eval_dur:.1f}s.")

    labels_arr = np.array(all_labels, dtype=np.int32)
    scores_arr = np.array(all_scores, dtype=np.float32)

    # Compute Metrics using MetricEngine
    metric_engine = MetricEngine()
    metrics = metric_engine.compute_metrics(labels_arr, scores_arr, threshold=0.5)

    bonafide_count = int(np.sum(labels_arr == 0))
    spoof_count = int(np.sum(labels_arr == 1))

    eval_results = {
        "status": "COMPLETED",
        "dataset": "ASVspoof 2019 Logical Access (LA) Evaluation Set",
        "checkpoint_evaluated": abs_ckpt_path,
        "checkpoint_sha256": ckpt_audit['sha256_hash'],
        "checkpoint_provenance": ckpt_audit['provenance'],
        "sample_count": metrics.sample_count,
        "bonafide_count": bonafide_count,
        "spoof_count": spoof_count,
        "eer": metrics.eer,
        "eer_threshold": round(float(metrics.eer_threshold), 4) if metrics.eer_threshold is not None else None,
        "roc_auc": metrics.roc_auc,
        "accuracy": metrics.accuracy,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "f1_score": metrics.f1_score,
        "far": metrics.far,
        "frr": metrics.frr,
        "confusion_matrix": metrics.confusion_matrix,
        "evaluation_duration_seconds": round(eval_dur, 2)
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    cm = metrics.confusion_matrix
    md_content = f"""# Phase 6: Real ASVspoof 2019 LA Evaluation Report

**Evaluation Status**: `COMPLETED`  
**Dataset Path**: `{abs_dataset_dir}`  
**Evaluated Checkpoint**: `{abs_ckpt_path}`  
**Checkpoint SHA-256**: `{ckpt_audit['sha256_hash']}`  
**Total Samples**: `{metrics.sample_count}` (`{bonafide_count}` bonafide, `{spoof_count}` spoof)  
**Evaluation Duration**: `{eval_dur:.1f}s`  

---

## 1. Measured Performance Metrics
- **Equal Error Rate (EER)**: `{metrics.eer:.4f}` ({metrics.eer * 100:.2f}%) at threshold `{metrics.eer_threshold:.4f}`
- **ROC-AUC**: `{metrics.roc_auc:.4f}`
- **Accuracy**: `{metrics.accuracy:.4f}` ({metrics.accuracy * 100:.2f}%)
- **Precision**: `{metrics.precision:.4f}`
- **Recall**: `{metrics.recall:.4f}`
- **F1 Score**: `{metrics.f1_score:.4f}`
- **False Acceptance Rate (FAR)**: `{metrics.far:.4f}` ({metrics.far * 100:.2f}%)
- **False Rejection Rate (FRR)**: `{metrics.frr:.4f}` ({metrics.frr * 100:.2f}%)

---

## 2. Confusion Matrix (at Default Operating Point 0.5)

| Metric | Count |
| :--- | :--- |
| **True Positives (Spoof Detected)** | `{cm['tp']}` |
| **True Negatives (Bonafide Accepted)** | `{cm['tn']}` |
| **False Positives (Bonafide Flagged as Spoof)** | `{cm['fp']}` |
| **False Negatives (Spoof Passed as Bonafide)** | `{cm['fn']}` |
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\nMeasured Metrics:")
    print(f"  - EER: {metrics.eer*100:.2f}% (Threshold: {metrics.eer_threshold:.4f})")
    print(f"  - ROC-AUC: {metrics.roc_auc:.4f}")
    print(f"  - Accuracy: {metrics.accuracy*100:.2f}%")
    print(f"  - F1 Score: {metrics.f1_score:.4f}")
    print(f"  - FAR: {metrics.far*100:.2f}%, FRR: {metrics.frr*100:.2f}%")
    print(f"Saved evaluation report to {report_path} and {json_path}")

    return eval_results


def main():
    parser = argparse.ArgumentParser(description="VoxShield Real ASVspoof Evaluation Script")
    parser.add_argument("--dataset-dir", type=str, default="datasets/ASVspoof2019_LA/LA")
    parser.add_argument("--checkpoint", type=str, default="models/asvspoof2019_la_resnet.pt")
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    evaluate_model(dataset_dir=args.dataset_dir, checkpoint_path=args.checkpoint, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
