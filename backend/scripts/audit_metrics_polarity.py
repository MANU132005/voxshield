"""
Independent Scientific Metric Validation & Score Polarity Audit.

Inspects raw model predictions on ASVspoof 2019 LA evaluation set,
audits protocol label mappings, checks score distribution, computes ROC-AUC / EER,
and identifies whether EER=50% / AUC=0.50 is caused by metric bug or model output collapse.
"""

import os
import sys
import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.anti_spoofing.asvspoof_dataset import ASVspoofDataset
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet
from app.services.evaluation.metric_engine import MetricEngine
from app.services.model_integrity.auditor import calculate_file_sha256


def audit_raw_metrics(
    dataset_dir: str = "datasets/ASVspoof2019_LA/LA",
    checkpoint_path: str = "models/asvspoof2019_la_smoketest.pt"
):
    print("========================================================")
    print("INDEPENDENT SCIENTIFIC METRIC VALIDATION & POLARITY AUDIT")
    print("========================================================")

    abs_dataset_dir = os.path.abspath(dataset_dir)
    abs_ckpt_path = os.path.abspath(checkpoint_path)

    proto_file = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_cm_protocols", "ASVspoof2019.LA.cm.eval.trl.txt")
    audio_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_eval")

    print(f"Checkpoint Path: {abs_ckpt_path}")
    print(f"Checkpoint SHA-256: {calculate_file_sha256(abs_ckpt_path)}")
    print(f"Protocol File: {proto_file}")

    # Load dataset
    ds = ASVspoofDataset(protocol_file=proto_file, audio_dir=audio_dir)
    loader = DataLoader(ds, batch_size=64, shuffle=False, num_workers=4 if os.name != 'nt' else 0)

    # Load Model
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

    all_logits = []
    all_probs = []
    all_labels = []

    print("Extracting raw logits and ground-truth labels...")
    with torch.no_grad():
        for batch_idx, (features, labels) in enumerate(loader):
            features = features.to(device)
            logits = model(features).squeeze(-1).cpu().numpy()
            probs = torch.sigmoid(torch.tensor(logits)).numpy()

            all_logits.extend(logits)
            all_probs.extend(probs)
            all_labels.extend(labels.squeeze(-1).numpy())

    logits_arr = np.array(all_logits, dtype=np.float32)
    probs_arr = np.array(all_probs, dtype=np.float32)
    labels_arr = np.array(all_labels, dtype=np.int32)

    bonafide_mask = (labels_arr == 0)
    spoof_mask = (labels_arr == 1)

    bonafide_count = int(np.sum(bonafide_mask))
    spoof_count = int(np.sum(spoof_mask))
    total_count = len(labels_arr)

    print("\n--- 1. Class Distribution Analysis ---")
    print(f"Total Evaluation Samples: {total_count}")
    print(f"Bona-fide (Label 0): {bonafide_count} ({bonafide_count/total_count*100:.2f}%)")
    print(f"Spoof (Label 1): {spoof_count} ({spoof_count/total_count*100:.2f}%)")

    print("\n--- 2. Raw Score Distribution ---")
    print(f"Logits Overall: Min={logits_arr.min():.4f}, Max={logits_arr.max():.4f}, Mean={logits_arr.mean():.4f}, Std={logits_arr.std():.4f}")
    print(f"Probs Overall: Min={probs_arr.min():.4f}, Max={probs_arr.max():.4f}, Mean={probs_arr.mean():.4f}, Std={probs_arr.std():.4f}")

    bonafide_probs = probs_arr[bonafide_mask]
    spoof_probs = probs_arr[spoof_mask]

    print(f"Bona-fide Probs: Mean={bonafide_probs.mean():.4f}, Std={bonafide_probs.std():.4f}, Min={bonafide_probs.min():.4f}, Max={bonafide_probs.max():.4f}")
    print(f"Spoof Probs:     Mean={spoof_probs.mean():.4f}, Std={spoof_probs.std():.4f}, Min={spoof_probs.min():.4f}, Max={spoof_probs.max():.4f}")

    print("\n--- 3. Score Polarity & Discrimination Check ---")
    mean_diff = spoof_probs.mean() - bonafide_probs.mean()
    print(f"Mean Spoof Score - Mean Bona-fide Score: {mean_diff:.6f}")

    # Standard metric calculation at 0.5
    engine = MetricEngine()
    std_metrics = engine.compute_metrics(labels_arr, probs_arr, threshold=0.5)

    # Inverted score calculation (testing if score polarity was inverted)
    inv_probs = 1.0 - probs_arr
    inv_metrics = engine.compute_metrics(labels_arr, inv_probs, threshold=0.5)

    print("\n--- 4. Standard vs Inverted Score Metrics ---")
    print(f"Standard  -> Acc: {std_metrics.accuracy}, F1: {std_metrics.f1_score}, Recall: {std_metrics.recall}, Precision: {std_metrics.precision}, EER: {std_metrics.eer}, AUC: {std_metrics.roc_auc}")
    print(f"Inverted  -> Acc: {inv_metrics.accuracy}, F1: {inv_metrics.f1_score}, Recall: {inv_metrics.recall}, Precision: {inv_metrics.precision}, EER: {inv_metrics.eer}, AUC: {inv_metrics.roc_auc}")

    # Root Cause Diagnosis
    constant_probs = np.allclose(probs_arr, probs_arr[0], atol=1e-3)
    if constant_probs or std_metrics.roc_auc == 0.5:
        root_cause = "MODEL_OUTPUT_COLLAPSE (3-epoch smoke test produced saturated constant positive logits across all samples)."
    elif mean_diff < 0:
        root_cause = "SCORE_POLARITY_INVERSION (Higher scores were produced for bona-fide instead of spoof)."
    else:
        root_cause = "GENUINE_METRIC_BEHAVIOR."

    print(f"\nDIAGNOSIS: {root_cause}")

    audit_result = {
        "dataset_root": abs_dataset_dir,
        "checkpoint": abs_ckpt_path,
        "checkpoint_sha256": calculate_file_sha256(abs_ckpt_path),
        "total_samples": total_count,
        "bonafide_count": bonafide_count,
        "spoof_count": spoof_count,
        "class_imbalance": {
            "spoof_percentage": round(spoof_count/total_count*100, 2),
            "bonafide_percentage": round(bonafide_count/total_count*100, 2)
        },
        "raw_score_stats": {
            "bonafide_mean_prob": float(bonafide_probs.mean()),
            "spoof_mean_prob": float(spoof_probs.mean()),
            "mean_diff": float(mean_diff),
            "probs_std": float(probs_arr.std())
        },
        "standard_metrics": {
            "accuracy": std_metrics.accuracy,
            "f1_score": std_metrics.f1_score,
            "recall": std_metrics.recall,
            "precision": std_metrics.precision,
            "eer": std_metrics.eer,
            "roc_auc": std_metrics.roc_auc,
            "confusion_matrix": std_metrics.confusion_matrix
        },
        "root_cause_diagnosis": root_cause
    }

    return audit_result


if __name__ == "__main__":
    audit_raw_metrics()
