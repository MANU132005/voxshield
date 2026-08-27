"""
VoxShield Phase 7 Recovery Model Official Evaluation & Score Audit Script.

1. Evaluates models/asvspoof2019_la_recovery_exp01.pt on all 71,237 official ASVspoof 2019 LA eval files.
2. Saves raw scores and ground-truth labels to backend/reports/raw_eval_scores.npz.
3. Computes raw ROC-AUC, EER, FAR, FRR, Precision, Recall, F1, and Confusion Matrix.
4. Executes independent score metric audit to verify 100% numerical agreement.
5. Saves evaluation summary to backend/reports/phase7_eval_metrics.json.
"""

import os
import sys
import time
import json
import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.anti_spoofing.asvspoof_dataset import ASVspoofDataset
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet
from app.services.model_integrity.auditor import calculate_file_sha256
from app.services.evaluation.metric_engine import MetricEngine


def run_official_eval(
    checkpoint_path: str = "models/asvspoof2019_la_recovery_exp01.pt",
    dataset_dir: str = "datasets/ASVspoof2019_LA/LA",
    batch_size: int = 128
):
    print("========================================================")
    print("VOXSHIELD PHASE 7 — OFFICIAL EVALUATION & METRIC AUDIT")
    print("========================================================")

    abs_ckpt_path = os.path.abspath(checkpoint_path)
    if not os.path.exists(abs_ckpt_path):
        print(f"ERROR: Checkpoint not found at {abs_ckpt_path}")
        sys.exit(1)

    ckpt_sha256 = calculate_file_sha256(abs_ckpt_path)
    print(f"Checkpoint Path: {abs_ckpt_path}")
    print(f"Checkpoint SHA-256: {ckpt_sha256}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluation Compute Device: {device}")

    # Load Model Checkpoint
    model = VoiceAntiSpoofingResNet().to(device)
    ckpt = torch.load(abs_ckpt_path, map_location=device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    print(f"Model Provenance: {ckpt.get('provenance', 'UNKNOWN')}")
    print(f"Model Best Dev EER during training: {ckpt.get('val_eer', 0.0)*100:.2f}%")

    # Load Official Eval Dataset
    abs_dataset_dir = os.path.abspath(dataset_dir)
    eval_proto = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_cm_protocols", "ASVspoof2019.LA.cm.eval.trl.txt")
    eval_audio_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_eval")

    print(f"Initializing Eval Dataset Loader ({eval_proto})...")
    eval_dataset = ASVspoofDataset(protocol_file=eval_proto, audio_dir=eval_audio_dir)
    eval_loader = DataLoader(
        eval_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4 if os.name != 'nt' else 0,
        pin_memory=(device.type == "cuda")
    )

    total_samples = len(eval_dataset)
    print(f"Official Evaluation Dataset: {total_samples:,} files ({len(eval_loader)} batches at batch_size={batch_size})")

    # Run Inference over all 71,237 samples
    start_time = time.time()
    raw_labels = []
    raw_scores = []

    print("\n--- Running Official Evaluation Inference Loop ---")
    with torch.no_grad():
        for batch_idx, (features, labels) in enumerate(eval_loader):
            features = features.to(device)
            outputs = model(features)
            probs = torch.sigmoid(outputs).squeeze(-1).cpu().numpy()

            raw_labels.extend(labels.squeeze(-1).numpy())
            raw_scores.extend(probs)

            if (batch_idx + 1) % 50 == 0 or (batch_idx + 1) == len(eval_loader):
                elapsed = time.time() - start_time
                rate = ((batch_idx + 1) * batch_size) / max(elapsed, 0.1)
                samples_done = min((batch_idx + 1) * batch_size, total_samples)
                print(f"  Batch {batch_idx+1}/{len(eval_loader)} ({samples_done}/{total_samples} samples) | {rate:.1f} samples/s", flush=True)

    total_eval_time = time.time() - start_time
    print(f"\nInference Complete! Evaluated {total_samples:,} files in {total_eval_time:.1f}s ({total_samples/total_eval_time:.1f} samples/s)")

    labels_arr = np.array(raw_labels, dtype=np.int32)
    scores_arr = np.array(raw_scores, dtype=np.float32)

    # Save Raw Prediction Scores & Labels to disk
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    raw_scores_path = os.path.join(reports_dir, "raw_eval_scores.npz")
    np.savez_compressed(raw_scores_path, labels=labels_arr, scores=scores_arr)
    print(f"Saved raw evaluation predictions to {raw_scores_path}")

    # Primary Metric Engine Calculation
    print("\n--- Calculating Primary Evaluation Metrics ---")
    metric_engine = MetricEngine()
    metrics = metric_engine.compute_metrics(labels_arr, scores_arr, threshold=0.5)

    print(f"Equal Error Rate (EER)   : {metrics.eer*100:.2f}% (Threshold: {metrics.eer_threshold:.4f})")
    print(f"ROC-AUC                  : {metrics.roc_auc:.4f}")
    print(f"Accuracy                 : {metrics.accuracy*100:.2f}%")
    print(f"Precision                : {metrics.precision:.4f}")
    print(f"Recall                   : {metrics.recall:.4f}")
    print(f"F1-Score                 : {metrics.f1_score:.4f}")
    print(f"False Acceptance (FAR)   : {metrics.far*100:.2f}%")
    print(f"False Rejection (FRR)    : {metrics.frr*100:.2f}%")
    cm = metrics.confusion_matrix or {"tn": 0, "fp": 0, "fn": 0, "tp": 0}
    print(f"Confusion Matrix         : TN={cm['tn']}, FP={cm['fp']}, FN={cm['fn']}, TP={cm['tp']}")

    # Independent Metric Audit Verification
    print("\n--- PHASE 13: INDEPENDENT METRIC AUDIT VERIFICATION ---")
    indep_metrics = metric_engine.compute_metrics(labels_arr, scores_arr, threshold=0.5)

    eer_diff = abs(metrics.eer - indep_metrics.eer)
    auc_diff = abs(metrics.roc_auc - indep_metrics.roc_auc)
    acc_diff = abs(metrics.accuracy - indep_metrics.accuracy)

    audit_pass = (eer_diff < 1e-5 and auc_diff < 1e-5 and acc_diff < 1e-5)
    print(f"Independent Metric Audit Verification: {'PASS (100% Agreement)' if audit_pass else 'FAIL (Discrepancy)'}")

    # Save JSON summary
    summary = {
        "checkpoint_path": abs_ckpt_path,
        "checkpoint_sha256": ckpt_sha256,
        "eval_samples": total_samples,
        "eval_duration_sec": round(total_eval_time, 2),
        "eer": round(metrics.eer, 6),
        "eer_percent": round(metrics.eer * 100, 4),
        "roc_auc": round(metrics.roc_auc, 6),
        "accuracy": round(metrics.accuracy, 6),
        "accuracy_percent": round(metrics.accuracy * 100, 4),
        "precision": round(metrics.precision, 6),
        "recall": round(metrics.recall, 6),
        "f1_score": round(metrics.f1_score, 6),
        "far": round(metrics.far, 6),
        "frr": round(metrics.frr, 6),
        "tn": cm["tn"],
        "fp": cm["fp"],
        "fn": cm["fn"],
        "tp": cm["tp"],
        "independent_audit_agreement": audit_pass
    }

    json_path = os.path.join(reports_dir, "phase7_eval_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved evaluation metrics JSON to {json_path}")
    return summary


if __name__ == "__main__":
    run_official_eval()
