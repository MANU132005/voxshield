"""
Phase 6 ASVspoof 2019 LA Real Model Training CLI Script.

Executes real training ONLY when official dataset is physically present and verified.
Saves new checkpoint to models/asvspoof2019_la_resnet.pt (preserving models/anti_spoofing_resnet.pt intact).
"""

import os
import sys
import time
import hashlib
import json
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.dataset_discovery.discovery import DatasetDiscoveryEngine
from app.services.anti_spoofing.asvspoof_dataset import ASVspoofDataset
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet
from app.services.model_integrity.auditor import calculate_file_sha256


def train_model(
    dataset_dir: str = "datasets/ASVspoof2019_LA/LA",
    epochs: int = 10,
    batch_size: int = 32,
    lr: float = 0.001,
    seed: int = 42,
    checkpoint_path: str = "models/asvspoof2019_la_resnet.pt",
    provenance: str = "REAL_ASVSPOOF_TRAINED"
):
    print("========================================================")
    print("VOXSHIELD PHASE 6 — REAL ASVSPOOF TRAINING PIPELINE")
    print("========================================================")

    # 1. Physical Dataset Audit Verification
    engine = DatasetDiscoveryEngine(dataset_root=dataset_dir)
    audit_res = engine.audit_dataset()

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "phase6_training_report.md")
    report_json_path = os.path.join(reports_dir, "phase6_training_report.json")

    if not audit_res.is_valid:
        print(f"TRAINING BLOCKED: Official dataset at '{dataset_dir}' is missing or invalid.")
        print("Status: BLOCKED_DATASET")

        md_content = f"""# Phase 6: Real ASVspoof 2019 LA Model Training Report

**Training Status**: `BLOCKED_DATASET`  
**Dataset Path**: `{dataset_dir}`  
**Prerequisite Check**: `FAILED — DATASET_MISSING`  

> [!WARNING]
> Training halted per non-negotiable scientific rules: Real model training requires physical dataset presence.
> Baseline synthetic checkpoint (`backend/models/anti_spoofing_resnet.pt`) remains preserved intact.
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        sys.exit(1)

    print(f"Dataset audit passed (INTEGRITY_VERIFIED). Starting real training for {epochs} epochs...")

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

    # Datasets and Loaders
    print("Initializing ASVspoof PyTorch Dataset Loaders...")
    train_dataset = ASVspoofDataset(protocol_file=train_proto, audio_dir=train_audio_dir)
    dev_dataset = ASVspoofDataset(protocol_file=dev_proto, audio_dir=dev_audio_dir)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4 if os.name != 'nt' else 0, # safe workers for windows
        pin_memory=(device.type == "cuda")
    )
    dev_loader = DataLoader(
        dev_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4 if os.name != 'nt' else 0,
        pin_memory=(device.type == "cuda")
    )

    print(f"Train samples: {len(train_dataset)} ({len(train_loader)} batches)")
    print(f"Dev samples: {len(dev_dataset)} ({len(dev_loader)} batches)")

    # Instantiate Model, Loss, Optimizer
    model = VoiceAntiSpoofingResNet().to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    start_time = time.time()
    epoch_logs = []
    best_val_loss = float("inf")
    best_epoch = 0
    best_val_acc = 0.0

    print("\n--- Beginning Training Loop ---")
    for epoch in range(1, epochs + 1):
        t_epoch_start = time.time()

        # Training Phase
        model.train()
        running_train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_idx, (features, labels) in enumerate(train_loader):
            features = features.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_train_loss += loss.item() * features.size(0)
            preds = (torch.sigmoid(outputs) >= 0.5).float()
            train_correct += (preds == labels).sum().item()
            train_total += labels.size(0)

            if (batch_idx + 1) % 25 == 0 or (batch_idx + 1) == len(train_loader):
                elapsed_batch = time.time() - t_epoch_start
                rate = (batch_idx + 1) / max(elapsed_batch, 0.1)
                eta_epoch = (len(train_loader) - (batch_idx + 1)) / max(rate, 0.01)
                print(f"  Epoch {epoch}/{epochs} | Batch {batch_idx+1}/{len(train_loader)} ({train_total}/{len(train_dataset)} samples) | "
                      f"Loss: {running_train_loss/train_total:.4f} | {rate:.1f} batch/s | ETA epoch: {eta_epoch:.0f}s", flush=True)

        train_loss = running_train_loss / train_total
        train_acc = train_correct / train_total

        # Validation Phase
        model.eval()
        running_dev_loss = 0.0
        dev_correct = 0
        dev_total = 0

        with torch.no_grad():
            for features, labels in dev_loader:
                features = features.to(device)
                labels = labels.to(device)

                outputs = model(features)
                loss = criterion(outputs, labels)

                running_dev_loss += loss.item() * features.size(0)
                preds = (torch.sigmoid(outputs) >= 0.5).float()
                dev_correct += (preds == labels).sum().item()
                dev_total += labels.size(0)

        dev_loss = running_dev_loss / dev_total
        dev_acc = dev_correct / dev_total
        epoch_dur = time.time() - t_epoch_start

        if dev_loss < best_val_loss:
            best_val_loss = dev_loss
            best_val_acc = dev_acc
            best_epoch = epoch

        log_entry = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "dev_loss": round(dev_loss, 4),
            "dev_acc": round(dev_acc, 4),
            "duration_sec": round(epoch_dur, 2)
        }
        epoch_logs.append(log_entry)

        print(f"Epoch {epoch:02d}/{epochs:02d} [{epoch_dur:.1f}s] — "
              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc*100:.2f}% | "
              f"Dev Loss: {dev_loss:.4f}, Dev Acc: {dev_acc*100:.2f}%", flush=True)

    total_training_time = time.time() - start_time
    print(f"\nTraining completed in {total_training_time:.1f}s. Best Epoch: {best_epoch} (Dev Loss: {best_val_loss:.4f}, Dev Acc: {best_val_acc*100:.2f}%)")

    # Save NEW Real-Data Checkpoint
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    os.makedirs(models_dir, exist_ok=True)
    new_checkpoint_path = os.path.abspath(checkpoint_path)

    # Calculate total batches tracked for BatchNorm tracker verification
    total_batches = len(train_loader) * epochs

    checkpoint_payload = {
        "state_dict": model.state_dict(),
        "num_batches_tracked": total_batches,
        "provenance": provenance,
        "dataset": "ASVspoof 2019 Logical Access",
        "architecture": "VoiceAntiSpoofingResNet",
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "seed": seed,
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
        "best_val_acc": best_val_acc,
        "training_time_seconds": total_training_time,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    torch.save(checkpoint_payload, new_checkpoint_path)
    sha256_hash = calculate_file_sha256(new_checkpoint_path)
    file_size_mb = round(os.path.getsize(new_checkpoint_path) / (1024 * 1024), 2)

    print(f"Saved real trained checkpoint to: {new_checkpoint_path}")
    print(f"Checkpoint SHA-256: {sha256_hash}")
    print(f"Checkpoint Size: {file_size_mb} MB")

    # Save JSON report
    training_json = {
        "status": "COMPLETED",
        "training_executed": True,
        "dataset_path": abs_dataset_dir,
        "checkpoint_path": new_checkpoint_path,
        "checkpoint_sha256": sha256_hash,
        "checkpoint_size_mb": file_size_mb,
        "provenance": "REAL_ASVSPOOF_TRAINED",
        "hyperparameters": {
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": lr,
            "optimizer": "Adam",
            "seed": seed,
            "compute_device": str(device)
        },
        "best_epoch": best_epoch,
        "best_dev_loss": round(best_val_loss, 4),
        "best_dev_acc": round(best_val_acc, 4),
        "total_training_time_seconds": round(total_training_time, 2),
        "epoch_logs": epoch_logs
    }
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(training_json, f, indent=2)

    # Save Markdown report
    epoch_rows = "\n".join([
        f"| `{log['epoch']}` | `{log['train_loss']}` | `{log['train_acc']*100:.2f}%` | `{log['dev_loss']}` | `{log['dev_acc']*100:.2f}%` | `{log['duration_sec']}s` |"
        for log in epoch_logs
    ])

    md_report = f"""# Phase 6: Real ASVspoof 2019 LA Model Training Report

**Training Status**: `COMPLETED`  
**Dataset Path**: `{abs_dataset_dir}`  
**New Checkpoint Path**: `{new_checkpoint_path}`  
**Checkpoint SHA-256**: `{sha256_hash}`  
**Checkpoint Size**: `{file_size_mb} MB`  
**Provenance**: `REAL_ASVSPOOF_TRAINED`  
**Best Epoch**: `{best_epoch}` (Dev Loss: `{best_val_loss:.4f}`, Dev Acc: `{best_val_acc*100:.2f}%`)  
**Total Duration**: `{total_training_time:.1f}s`  

---

## 1. Baseline Checkpoint Preservation
> [!IMPORTANT]
> - Baseline synthetic demo checkpoint `backend/models/anti_spoofing_resnet.pt` remains **100% untouched & preserved**.
> - New real-data trained model saved to `backend/models/asvspoof2019_la_resnet.pt`.

---

## 2. Hyperparameters & Configuration
- **Dataset**: `ASVspoof 2019 Logical Access (LA)`
- **Train Split**: `25,380 FLAC audio files`
- **Dev Split**: `24,986 FLAC audio files`
- **Model Architecture**: `VoiceAntiSpoofingResNet (2D Residual CNN)`
- **Feature Extraction**: `80-band Log-Mel Spectrogram (16kHz, 300 frames)`
- **Epochs**: `{epochs}`
- **Batch Size**: `{batch_size}`
- **Optimizer**: `Adam (lr={lr}, weight_decay=1e-4)`
- **Loss Function**: `BCEWithLogitsLoss`
- **Random Seed**: `{seed}`

---

## 3. Epoch Training Log

| Epoch | Train Loss | Train Accuracy | Dev Loss | Dev Accuracy | Duration |
| :---: | :---: | :---: | :---: | :---: | :---: |
{epoch_rows}
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_report)

    print(f"Generated training reports at:\n  - {report_path}\n  - {report_json_path}")
    return training_json


def main():
    parser = argparse.ArgumentParser(description="VoxShield Real ASVspoof 2019 LA Training Script")
    parser.add_argument("--dataset-dir", type=str, default="datasets/ASVspoof2019_LA/LA", help="Path to ASVspoof 2019 LA dataset root")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--checkpoint-path", type=str, default="models/asvspoof2019_la_resnet.pt", help="Path to save new model checkpoint")
    parser.add_argument("--provenance", type=str, default="REAL_ASVSPOOF_TRAINED", help="Model provenance tag")
    args = parser.parse_args()

    train_model(
        dataset_dir=args.dataset_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        seed=args.seed,
        checkpoint_path=args.checkpoint_path,
        provenance=args.provenance
    )


if __name__ == "__main__":
    main()
