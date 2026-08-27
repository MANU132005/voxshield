"""
PyTorch Voice Anti-Spoofing Training & Evaluation Script.

Trains VoiceAntiSpoofingResNet on standardized Log-Mel Spectrogram features
and evaluates performance on held-out test data (Accuracy, EER, ROC-AUC, Precision, Recall, F1).
Exports trained weights to backend/models/anti_spoofing_resnet.pt.
"""

import os
import sys
import io
import math
import random
import numpy as np
import scipy.io.wavfile
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support, confusion_matrix

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.audio.processor import AudioProcessor
from app.services.audio.features import FeatureExtractor
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def generate_synthetic_audio_sample(is_spoof: bool, duration: float = 1.5, sample_rate: int = 16000) -> bytes:
    """
    Generates synthetic audio signal in memory.
    Genuine human voice: Natural harmonic fundamentals (120-240Hz) with smooth pitch contour & formant structures.
    Spoofed AI clone: High-frequency vocoder phase artifacts, metallic spectral ripple, and unnatural pitch stability.
    """
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    if not is_spoof:
        # Genuine human voice simulation: 150 Hz pitch with natural vibrato and formants
        pitch = 150.0 + 5.0 * np.sin(2 * np.pi * 3.5 * t)
        phase = 2 * np.pi * np.cumsum(pitch) / sample_rate
        signal = 0.6 * np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.15 * np.sin(3 * phase)
        # Add subtle breath noise
        noise = 0.01 * np.random.randn(n_samples)
        signal += noise
    else:
        # Spoofed AI clone simulation: Constant robotic pitch (150 Hz) + vocoder phase buzz & high-freq noise
        pitch = 150.0
        phase = 2 * np.pi * pitch * t
        signal = 0.6 * np.sin(phase) + 0.25 * np.sign(np.sin(2 * phase))  # Rectified square harmonics
        # Vocoder artifact noise in 4kHz-8kHz band
        vocoder_buzz = 0.08 * np.sin(2 * np.pi * 6500.0 * t) + 0.03 * np.random.randn(n_samples)
        signal += vocoder_buzz

    # Scale to int16
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.8
    int16_signal = (signal * 32767).astype(np.int16)

    buf = io.BytesIO()
    scipy.io.wavfile.write(buf, sample_rate, int16_signal)
    return buf.getvalue()


class CachedFeatureDataset(Dataset):
    def __init__(self, features_list, labels_list, target_frames: int = 300):
        self.samples = []
        for feat, label in zip(features_list, labels_list):
            log_mel = feat  # Shape (80, T)
            n_mels, n_frames = log_mel.shape

            # Standardize frame length to target_frames (300)
            if n_frames < target_frames:
                pad_width = target_frames - n_frames
                log_mel_norm = np.pad(log_mel, ((0, 0), (0, pad_width)), mode="constant", constant_values=-23.0)
            elif n_frames > target_frames:
                start = (n_frames - target_frames) // 2
                log_mel_norm = log_mel[:, start:start + target_frames]
            else:
                log_mel_norm = log_mel

            # Channel Z-score normalization
            mean = np.mean(log_mel_norm)
            std = np.std(log_mel_norm) + 1e-7
            log_mel_norm = (log_mel_norm - mean) / std

            tensor = torch.from_numpy(log_mel_norm).float().unsqueeze(0)  # Shape (1, 80, 300)
            target = torch.tensor([float(label)], dtype=torch.float32)
            self.samples.append((tensor, target))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def compute_eer(labels, scores):
    """Computes Equal Error Rate (EER) where FAR == FRR."""
    labels = np.array(labels)
    scores = np.array(scores)

    # Threshold search across score range
    thresholds = np.linspace(0.0, 1.0, 1001)
    min_diff = 1.0
    eer = 0.5

    for th in thresholds:
        far = np.mean(scores[labels == 0] >= th)  # False Accept Rate (Genuine classified as Spoof)
        frr = np.mean(scores[labels == 1] < th)   # False Reject Rate (Spoof classified as Genuine)
        diff = abs(far - frr)
        if diff < min_diff:
            min_diff = diff
            eer = (far + frr) / 2.0

    return float(eer)


def run_training():
    set_seed(42)
    print("=== VOXSHIELD MILESTONE 5: MODEL TRAINING ===")

    processor = AudioProcessor(target_sample_rate=16000, min_duration_seconds=0.5)
    feature_extractor = FeatureExtractor(sample_rate=16000)

    # 1. Dataset Generation & Pre-caching
    num_samples_per_class = 200
    print(f"Extracting features for {num_samples_per_class * 2} audio samples...")

    features_list = []
    labels_list = []

    for _ in range(num_samples_per_class):
        # Genuine sample (Label 0)
        wav_gen = generate_synthetic_audio_sample(is_spoof=False, duration=1.5)
        proc_gen = processor.load_and_preprocess(wav_gen, "genuine.wav")
        feat_gen = feature_extractor.extract_features(proc_gen)
        features_list.append(feat_gen.log_mel_spectrogram)
        labels_list.append(0)

        # Spoofed sample (Label 1)
        wav_spf = generate_synthetic_audio_sample(is_spoof=True, duration=1.5)
        proc_spf = processor.load_and_preprocess(wav_spf, "spoof.wav")
        feat_spf = feature_extractor.extract_features(proc_spf)
        features_list.append(feat_spf.log_mel_spectrogram)
        labels_list.append(1)

    # 2. Leakage-safe Train/Val/Test Split (70% Train, 15% Val, 15% Test)
    indices = list(range(len(labels_list)))
    random.shuffle(indices)

    train_cutoff = int(0.70 * len(indices))
    val_cutoff = int(0.85 * len(indices))

    train_idx = indices[:train_cutoff]
    val_idx = indices[train_cutoff:val_cutoff]
    test_idx = indices[val_cutoff:]

    train_dataset = CachedFeatureDataset([features_list[i] for i in train_idx], [labels_list[i] for i in train_idx])
    val_dataset = CachedFeatureDataset([features_list[i] for i in val_idx], [labels_list[i] for i in val_idx])
    test_dataset = CachedFeatureDataset([features_list[i] for i in test_idx], [labels_list[i] for i in test_idx])

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    print(f"Dataset split: Train={len(train_dataset)}, Val={len(val_dataset)}, Test={len(test_dataset)}")

    # 3. Model, Loss, Optimizer Initialization
    model = VoiceAntiSpoofingResNet()
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

    # 4. Training Loop
    best_val_loss = float("inf")
    best_state_dict = None
    epochs = 8

    print("\nBeginning PyTorch ResNet-18 Training...")
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0

        for inputs, targets in train_loader:
            optimizer.zero_grad()
            logits = model(inputs)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * inputs.size(0)

        train_loss /= len(train_dataset)

        # Validation Loop
        model.eval()
        val_loss = 0.0
        val_targets_all = []
        val_scores_all = []

        with torch.no_grad():
            for inputs, targets in val_loader:
                logits = model(inputs)
                loss = criterion(logits, targets)
                val_loss += loss.item() * inputs.size(0)
                probs = torch.sigmoid(logits)

                val_targets_all.extend(targets.squeeze(-1).numpy())
                val_scores_all.extend(probs.squeeze(-1).numpy())

        val_loss /= len(val_dataset)
        val_eer = compute_eer(val_targets_all, val_scores_all)

        print(f"Epoch [{epoch}/{epochs}] - Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val EER: {val_eer:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state_dict = model.state_dict().copy()

    # 5. Export Best Model Weights
    models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    os.makedirs(models_dir, exist_ok=True)
    model_save_path = os.path.join(models_dir, "anti_spoofing_resnet.pt")

    torch.save(best_state_dict, model_save_path)
    print(f"\nSuccessfully exported best trained PyTorch weights to: {model_save_path}")

    # 6. Evaluation on Held-out Test Set
    model.load_state_dict(best_state_dict)
    model.eval()

    test_targets_all = []
    test_scores_all = []

    with torch.no_grad():
        for inputs, targets in test_loader:
            logits = model(inputs)
            probs = torch.sigmoid(logits)
            test_targets_all.extend(targets.squeeze(-1).numpy())
            test_scores_all.extend(probs.squeeze(-1).numpy())

    test_targets = np.array(test_targets_all)
    test_scores = np.array(test_scores_all)
    test_preds = (test_scores >= 0.50).astype(int)

    acc = np.mean(test_preds == test_targets)
    precision, recall, f1, _ = precision_recall_fscore_support(test_targets, test_preds, average="binary")
    auc = roc_auc_score(test_targets, test_scores)
    eer = compute_eer(test_targets, test_scores)
    cm = confusion_matrix(test_targets, test_preds)

    print("\n=== HELD-OUT TEST SET EVALUATION RESULTS ===")
    print(f"Test Accuracy : {acc * 100:.2f}%")
    print(f"Precision     : {precision:.4f}")
    print(f"Recall        : {recall:.4f}")
    print(f"F1-Score      : {f1:.4f}")
    print(f"ROC-AUC       : {auc:.4f}")
    print(f"Equal Error Rate (EER) : {eer * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(f"  TN={cm[0,0]} (True Genuine)  | FP={cm[0,1]} (False Alarm)")
    print(f"  FN={cm[1,0]} (Missed Spoof)  | TP={cm[1,1]} (Detected Spoof)")


if __name__ == "__main__":
    run_training()
