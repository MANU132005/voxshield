"""
VoxShield Master Forensic Audit Suite (Phases 1 through 6).

Executes fast, thorough, read-only empirical verification of:
Phase 1: Dataset & File Integrity
Phase 2: Protocol & Label Integrity
Phase 3: Preprocessing & Feature Extraction Integrity
Phase 4: Model Architecture & Gradient Flow Integrity
Phase 5: Loss Function & Class Imbalance Analysis
Phase 6: Cheap Real-Data Learning Health Check
"""

import os
import sys
import hashlib
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, WeightedRandomSampler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.dataset_discovery.discovery import DatasetDiscoveryEngine
from app.services.anti_spoofing.asvspoof_dataset import ASVspoofDataset
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet
from app.services.evaluation.metric_engine import MetricEngine


def run_forensic_audit_suite(dataset_dir: str = "datasets/ASVspoof2019_LA/LA"):
    print("========================================================")
    print("VOXSHIELD MASTER FORENSIC AUDIT SUITE (PHASES 1–6)")
    print("========================================================")

    results = {}
    abs_dataset_dir = os.path.abspath(dataset_dir)
    proto_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_cm_protocols")

    # ---------------------------------------------------------
    # PHASE 1: DATASET & FILE INTEGRITY AUDIT
    # ---------------------------------------------------------
    print("\n--- PHASE 1: DATASET & FILE INTEGRITY AUDIT ---")
    engine = DatasetDiscoveryEngine(dataset_root=dataset_dir)
    audit_res = engine.audit_dataset()

    print(f"Dataset Root: {abs_dataset_dir}")
    print(f"Protocol Check: Valid={audit_res.is_valid}")

    train_proto = os.path.join(proto_dir, "ASVspoof2019.LA.cm.train.trn.txt")
    dev_proto = os.path.join(proto_dir, "ASVspoof2019.LA.cm.dev.trl.txt")
    eval_proto = os.path.join(proto_dir, "ASVspoof2019.LA.cm.eval.trl.txt")

    train_audio_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_train")
    dev_audio_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_dev")
    eval_audio_dir = os.path.join(abs_dataset_dir, "ASVspoof2019_LA_eval")

    # Load datasets
    train_dataset = ASVspoofDataset(protocol_file=train_proto, audio_dir=train_audio_dir)
    dev_dataset = ASVspoofDataset(protocol_file=dev_proto, audio_dir=dev_audio_dir)
    eval_dataset = ASVspoofDataset(protocol_file=eval_proto, audio_dir=eval_audio_dir)

    print(f"Train Protocol Records: {len(train_dataset.samples)}")
    print(f"Dev Protocol Records: {len(dev_dataset.samples)}")
    print(f"Eval Protocol Records: {len(eval_dataset.samples)}")

    # Check Speaker Overlap
    train_speakers = set(s[0] for s in train_dataset.samples)
    dev_speakers = set(s[0] for s in dev_dataset.samples)
    eval_speakers = set(s[0] for s in eval_dataset.samples)

    train_dev_spk_overlap = train_speakers.intersection(dev_speakers)
    train_eval_spk_overlap = train_speakers.intersection(eval_speakers)
    dev_eval_spk_overlap = dev_speakers.intersection(eval_speakers)

    print(f"Train Unique Speakers: {len(train_speakers)}")
    print(f"Dev Unique Speakers: {len(dev_speakers)}")
    print(f"Eval Unique Speakers: {len(eval_speakers)}")
    print(f"Speaker Overlap (Train/Dev): {len(train_dev_spk_overlap)}")
    print(f"Speaker Overlap (Train/Eval): {len(train_eval_spk_overlap)}")
    print(f"Speaker Overlap (Dev/Eval): {len(dev_eval_spk_overlap)}")

    phase1_pass = (
        len(train_dataset) == 25380 and
        len(dev_dataset) == 24844 and
        len(eval_dataset) == 71237 and
        len(train_dev_spk_overlap) == 0 and
        len(train_eval_spk_overlap) == 0 and
        len(dev_eval_spk_overlap) == 0
    )
    print(f"-> PHASE 1 AUDIT RESULT: {'PASS' if phase1_pass else 'FAIL'}")
    results["phase1"] = "PASS" if phase1_pass else "FAIL"

    # ---------------------------------------------------------
    # PHASE 2: PROTOCOL & LABEL FORENSICS
    # ---------------------------------------------------------
    print("\n--- PHASE 2: PROTOCOL & LABEL FORENSICS ---")
    train_labels = [s[3] for s in train_dataset.samples]
    dev_labels = [s[3] for s in dev_dataset.samples]
    eval_labels = [s[3] for s in eval_dataset.samples]

    train_bf = sum(1 for l in train_labels if l == 0)
    train_sp = sum(1 for l in train_labels if l == 1)
    dev_bf = sum(1 for l in dev_labels if l == 0)
    dev_sp = sum(1 for l in dev_labels if l == 1)
    eval_bf = sum(1 for l in eval_labels if l == 0)
    eval_sp = sum(1 for l in eval_labels if l == 1)

    print(f"Train Split: Bonafide={train_bf} ({train_bf/len(train_labels)*100:.2f}%), Spoof={train_sp} ({train_sp/len(train_labels)*100:.2f}%)")
    print(f"Dev Split  : Bonafide={dev_bf} ({dev_bf/len(dev_labels)*100:.2f}%), Spoof={dev_sp} ({dev_sp/len(dev_labels)*100:.2f}%)")
    print(f"Eval Split : Bonafide={eval_bf} ({eval_bf/len(eval_labels)*100:.2f}%), Spoof={eval_sp} ({eval_sp/len(eval_labels)*100:.2f}%)")

    # Polarity verification: bonafide -> 0, spoof -> 1
    # Higher score -> P(spoof = 1) -> Spoof
    phase2_pass = (train_bf == 2580 and train_sp == 22800 and dev_bf == 2548 and dev_sp == 22296 and eval_bf == 7355 and eval_sp == 63882)
    print(f"-> PHASE 2 AUDIT RESULT: {'PASS' if phase2_pass else 'FAIL'}")
    results["phase2"] = "PASS" if phase2_pass else "FAIL"

    # ---------------------------------------------------------
    # PHASE 3: PREPROCESSING / FEATURE FORENSICS
    # ---------------------------------------------------------
    print("\n--- PHASE 3: PREPROCESSING & FEATURE FORENSICS ---")
    feat_sample, label_sample = train_dataset[0]
    print(f"Feature Tensor Shape: {feat_sample.shape} (dtype: {feat_sample.dtype})")
    print(f"Feature Tensor Stats: Mean={feat_sample.mean().item():.4f}, Std={feat_sample.std().item():.4f}, Min={feat_sample.min().item():.4f}, Max={feat_sample.max().item():.4f}")
    has_nan_inf = torch.isnan(feat_sample).any().item() or torch.isinf(feat_sample).any().item()
    print(f"NaN / Inf check: {'FAIL (NaN/Inf present)' if has_nan_inf else 'PASS (No NaN/Inf)'}")

    phase3_pass = (feat_sample.shape == torch.Size([1, 80, 300]) and not has_nan_inf)
    print(f"-> PHASE 3 AUDIT RESULT: {'PASS' if phase3_pass else 'FAIL'}")
    results["phase3"] = "PASS" if phase3_pass else "FAIL"

    # ---------------------------------------------------------
    # PHASE 4: MODEL ARCHITECTURE FORENSICS
    # ---------------------------------------------------------
    print("\n--- PHASE 4: MODEL ARCHITECTURE FORENSICS ---")
    model = VoiceAntiSpoofingResNet()
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())

    print(f"Model Class: VoiceAntiSpoofingResNet")
    print(f"Total Parameters: {total_params:,}")
    print(f"Trainable Parameters: {trainable_params:,}")

    # Forward pass test
    dummy_input = torch.randn(4, 1, 80, 300)
    dummy_out = model(dummy_input)
    print(f"Dummy Input (4, 1, 80, 300) -> Output Shape: {dummy_out.shape}")

    phase4_pass = (total_params == 1223777 and dummy_out.shape == torch.Size([4, 1]))
    print(f"-> PHASE 4 AUDIT RESULT: {'PASS' if phase4_pass else 'FAIL'}")
    results["phase4"] = "PASS" if phase4_pass else "FAIL"

    # ---------------------------------------------------------
    # PHASE 5: TRAINING PIPELINE FORENSICS & SAMPLER ANALYSIS
    # ---------------------------------------------------------
    print("\n--- PHASE 5: TRAINING PIPELINE & CLASS BALANCING FORENSICS ---")
    weight_bf = 1.0 / train_bf
    weight_sp = 1.0 / train_sp
    sample_weights = [weight_bf if l == 0 else weight_sp for l in train_labels]
    sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(train_labels), replacement=True)
    balanced_loader = DataLoader(train_dataset, batch_size=32, sampler=sampler)

    # Inspect first batch class composition
    first_batch_feats, first_batch_labels = next(iter(balanced_loader))
    b_bf = (first_batch_labels == 0).sum().item()
    b_sp = (first_batch_labels == 1).sum().item()
    print(f"Balanced Sampler First Batch (Size 32): Bonafide={b_bf}, Spoof={b_sp}")

    phase5_pass = (b_bf > 0 and b_sp > 0)
    print(f"-> PHASE 5 AUDIT RESULT: {'PASS' if phase5_pass else 'FAIL'}")
    results["phase5"] = "PASS" if phase5_pass else "FAIL"

    # ---------------------------------------------------------
    # PHASE 6: CHEAP REAL-DATA LEARNING HEALTH CHECK
    # ---------------------------------------------------------
    print("\n--- PHASE 6: CHEAP REAL-DATA LEARNING HEALTH CHECK ---")
    device = torch.device("cpu")
    model = VoiceAntiSpoofingResNet().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    criterion = nn.BCEWithLogitsLoss()

    health_loader = DataLoader(train_dataset, batch_size=10, shuffle=True)
    feats, lbls = next(iter(health_loader))
    feats, lbls = feats.to(device), lbls.to(device)

    # Initial forward pass
    model.train()
    optimizer.zero_grad()
    initial_logits = model(feats)
    initial_loss = criterion(initial_logits, lbls)

    # Backward pass
    initial_loss.backward()
    grad_norms = [p.grad.norm().item() for p in model.parameters() if p.grad is not None]
    non_zero_grads = sum(1 for g in grad_norms if g > 1e-7)

    # Optimizer step
    optimizer.step()
    post_logits = model(feats)
    post_loss = criterion(post_logits, lbls)

    print(f"Initial Loss (10 real samples): {initial_loss.item():.4f}")
    print(f"Post-Step Loss (10 real samples): {post_loss.item():.4f}")
    print(f"Total Parameter Tensors: {len(list(model.parameters()))}")
    print(f"Non-Zero Gradient Tensors: {non_zero_grads}/{len(grad_norms)}")
    print(f"Initial Logit Mean={initial_logits.mean().item():.4f}, Std={initial_logits.std().item():.4f}")

    phase6_pass = (
        initial_loss.item() > 0 and
        post_loss.item() < initial_loss.item() and
        non_zero_grads == len(grad_norms) and
        initial_logits.std().item() > 1e-4
    )
    print(f"-> PHASE 6 HEALTH CHECK RESULT: {'PASS' if phase6_pass else 'FAIL'}")
    results["phase6"] = "PASS" if phase6_pass else "FAIL"

    print("\n========================================================")
    print("MASTER FORENSIC AUDIT SUITE (PHASES 1–6) SUMMARY")
    print("========================================================")
    for k, v in results.items():
        print(f"{k.upper()}: {v}")

    return results


if __name__ == "__main__":
    run_forensic_audit_suite()
