"""
Phase 7 Model Discrimination Recovery Training Script.

Executes controlled real ASVspoof 2019 LA training using WeightedRandomSampler
and tuned learning rate to recover genuine bonafide-vs-spoof discrimination.

Saves new checkpoint to models/asvspoof2019_la_recovery_exp01.pt.
Preserves existing checkpoints completely untouched.
"""

import os
import sys
import time
import json
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, WeightedRandomSampler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.dataset_discovery.discovery import DatasetDiscoveryEngine
from app.services.anti_spoofing.asvspoof_dataset import ASVspoofDataset
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet
from app.services.model_integrity.auditor import calculate_file_sha256
from app.services.evaluation.metric_engine import MetricEngine


def run_recovery_experiment(
    dataset_dir: str = "datasets/ASVspoof2019_LA/LA",
    epochs: int = 5,
    batch_size: int = 32,
    lr: float = 0.0001,
    seed: int = 42,
    checkpoint_path: str = "models/asvspoof2019_la_recovery_exp01.pt",
    provenance: str = "REAL_ASVSPOOF_RECOVERY_EXP01"
):
    print("========================================================")
    print("VOXSHIELD PHASE 7 — MODEL DISCRIMINATION RECOVERY (EXP01)")
    print("========================================================")

    # 1. Dataset Audit Verification
    engine = DatasetDiscoveryEngine(dataset_root=dataset_dir)
    audit_res = engine.audit_dataset()
    if not audit_res.is_valid:
        print(f"TRAINING BLOCKED: Dataset at '{dataset_dir}' is invalid/missing.")
        sys.exit(1)

    print(f"Dataset verified. Device setup...")

    # Reproducibility seed setup
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training Compute Device: {device}")

    # Paths
    abs_dataset_dir = os.path.abspath(dataset_dir)
    proto_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_cm_protocols")

    train_proto = os.path.join(proto_dir, "ASVspoof2019.LA.cm.train.trn.txt")
    dev_proto = os.path.join(proto_dir, "ASVspoof2019.LA.cm.dev.trl.txt")

    train_audio_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_train")
    dev_audio_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_dev")

    print("Initializing ASVspoof PyTorch Dataset Loaders...")
    train_dataset = ASVspoofDataset(protocol_file=train_proto, audio_dir=train_audio_dir)
    dev_dataset = ASVspoofDataset(protocol_file=dev_proto, audio_dir=dev_audio_dir)

    # Class Weights for WeightedRandomSampler to ensure 50/50 mini-batch balance
    labels = [sample[3] for sample in train_dataset.samples]
    bonafide_count = sum(1 for l in labels if l == 0)
    spoof_count = sum(1 for l in labels if l == 1)
    total_count = len(labels)

    print(f"Train Dataset Composition: {bonafide_count} Bonafide ({bonafide_count/total_count*100:.2f}%), {spoof_count} Spoof ({spoof_count/total_count*100:.2f}%)")

    weight_bonafide = 1.0 / bonafide_count
    weight_spoof = 1.0 / spoof_count
    sample_weights = [weight_bonafide if l == 0 else weight_spoof for l in labels]
    sampler = WeightedRandomSampler(weights=sample_weights, num_samples=total_count, replacement=True)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=4 if os.name != 'nt' else 0,
        pin_memory=(device.type == "cuda")
    )
    dev_loader = DataLoader(
        dev_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4 if os.name != 'nt' else 0,
        pin_memory=(device.type == "cuda")
    )

    # Model, Loss, Optimizer
    model = VoiceAntiSpoofingResNet().to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    metric_engine = MetricEngine()

    start_time = time.time()
    epoch_logs = []
    best_dev_eer = 1.0
    best_epoch = 0

    abs_ckpt_path = os.path.abspath(checkpoint_path)
    os.makedirs(os.path.dirname(abs_ckpt_path), exist_ok=True)

    print(f"\n--- Beginning Controlled Recovery Training ({epochs} Epochs) ---")
    for epoch in range(1, epochs + 1):
        t_epoch_start = time.time()

        # Train Phase
        model.train()
        running_train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_idx, (features, batch_labels) in enumerate(train_loader):
            features = features.to(device)
            batch_labels = batch_labels.to(device)

            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, batch_labels)
            loss.backward()
            optimizer.step()

            running_train_loss += loss.item() * features.size(0)
            preds = (torch.sigmoid(outputs) >= 0.5).float()
            train_correct += (preds == batch_labels).sum().item()
            train_total += batch_labels.size(0)

            if (batch_idx + 1) % 50 == 0 or (batch_idx + 1) == len(train_loader):
                elapsed_batch = time.time() - t_epoch_start
                rate = (batch_idx + 1) / max(elapsed_batch, 0.1)
                print(f"  Epoch {epoch}/{epochs} | Batch {batch_idx+1}/{len(train_loader)} | "
                      f"Train Loss: {running_train_loss/train_total:.4f} | {rate:.1f} batch/s", flush=True)

        train_loss = running_train_loss / train_total
        train_acc = train_correct / train_total

        # Validation Phase with ROC-AUC and EER
        model.eval()
        running_dev_loss = 0.0
        dev_labels_list = []
        dev_scores_list = []

        with torch.no_grad():
            for features, batch_labels in dev_loader:
                features = features.to(device)
                batch_labels = batch_labels.to(device)

                outputs = model(features)
                loss = criterion(outputs, batch_labels)
                probs = torch.sigmoid(outputs).squeeze(-1).cpu().numpy()

                running_dev_loss += loss.item() * features.size(0)
                dev_labels_list.extend(batch_labels.squeeze(-1).cpu().numpy())
                dev_scores_list.extend(probs)

        dev_loss = running_dev_loss / len(dev_labels_list)
        dev_labels_arr = np.array(dev_labels_list, dtype=np.int32)
        dev_scores_arr = np.array(dev_scores_list, dtype=np.float32)

        dev_metrics = metric_engine.compute_metrics(dev_labels_arr, dev_scores_arr, threshold=0.5)
        epoch_dur = time.time() - t_epoch_start

        log_entry = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "dev_loss": round(dev_loss, 4),
            "dev_acc": round(dev_metrics.accuracy, 4),
            "dev_eer": round(dev_metrics.eer, 4),
            "dev_roc_auc": round(dev_metrics.roc_auc, 4),
            "duration_sec": round(epoch_dur, 2)
        }
        epoch_logs.append(log_entry)

        print(f"Epoch {epoch:02d}/{epochs:02d} [{epoch_dur:.1f}s] — "
              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc*100:.2f}% | "
              f"Dev Loss: {dev_loss:.4f}, Dev Acc: {dev_metrics.accuracy*100:.2f}%, "
              f"Dev EER: {dev_metrics.eer*100:.2f}%, Dev ROC-AUC: {dev_metrics.roc_auc:.4f}", flush=True)

        if dev_metrics.eer < best_dev_eer:
            best_dev_eer = dev_metrics.eer
            best_epoch = epoch
            # Save Checkpoint
            torch.save({
                "epoch": epoch,
                "state_dict": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "val_loss": dev_loss,
                "val_eer": dev_metrics.eer,
                "val_roc_auc": dev_metrics.roc_auc,
                "provenance": provenance
            }, abs_ckpt_path)
            print(f"  --> Saved new best checkpoint to {abs_ckpt_path} (Dev EER: {dev_metrics.eer*100:.2f}%)")

    total_training_time = time.time() - start_time
    ckpt_sha256 = calculate_file_sha256(abs_ckpt_path)

    print("\n========================================================")
    print("TRAINING COMPLETED SUCCESSFULLY")
    print(f"Saved Checkpoint: {abs_ckpt_path}")
    print(f"Checkpoint SHA-256: {ckpt_sha256}")
    print(f"Best Epoch: {best_epoch} with Dev EER: {best_dev_eer*100:.2f}%")
    print(f"Total Training Time: {total_training_time:.1f}s")
    print("========================================================")

    return {
        "checkpoint_path": abs_ckpt_path,
        "checkpoint_sha256": ckpt_sha256,
        "provenance": provenance,
        "best_epoch": best_epoch,
        "best_dev_eer": best_dev_eer,
        "total_training_time": total_training_time,
        "epoch_logs": epoch_logs
    }


def main():
    parser = argparse.ArgumentParser(description="VoxShield Phase 7 Recovery Training Script")
    parser.add_argument("--dataset-dir", type=str, default="datasets/ASVspoof2019_LA/LA")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.0001)
    parser.add_argument("--checkpoint", type=str, default="models/asvspoof2019_la_recovery_exp01.pt")
    args = parser.parse_args()

    run_recovery_experiment(
        dataset_dir=args.dataset_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        checkpoint_path=args.checkpoint
    )


if __name__ == "__main__":
    main()
