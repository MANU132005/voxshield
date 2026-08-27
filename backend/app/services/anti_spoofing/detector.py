"""
AI Anti-Spoofing & Deepfake Voice Classifier Service.

Executes PyTorch neural inference using VoiceAntiSpoofingResNet to evaluate
probability score P(synthetic) from Log-Mel Spectrogram features.
"""

import os
import time
from dataclasses import dataclass
from typing import Optional, Union
import numpy as np
import torch
from app.services.audio.features import ExtractedFeatures
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet


@dataclass
class AntiSpoofingResult:
    synthetic_score: float      # Probability score [0.0 - 1.0] that speech is AI-generated
    is_synthetic: bool          # True if synthetic_score >= threshold (0.50)
    confidence: float           # Confidence magnitude [0.0 - 1.0]
    model_version: str          # Model version metadata
    inference_time_ms: float    # PyTorch forward pass duration in milliseconds


class AntiSpoofingDetector:
    def __init__(
        self,
        model_path: Optional[str] = None,
        target_frames: int = 300,  # ~3.0s window at 16kHz with 10ms hop
        decision_threshold: float = 0.50,
        model_version: str = "resnet18_logmel_v1.0"
    ):
        self.model_path = model_path
        self.target_frames = target_frames
        self.decision_threshold = decision_threshold
        self.model_version = model_version
        self.model: Optional[VoiceAntiSpoofingResNet] = None
        self._load_model()

    def _resolve_checkpoint(self) -> Optional[str]:
        """Resolves authoritative checkpoint path, prioritizing Phase 7 recovery model."""
        candidates = []
        if self.model_path:
            candidates.append(self.model_path)
        
        # Priority order: Recovery Exp01 -> Real ResNet -> Baseline
        candidates.extend([
            "models/asvspoof2019_la_recovery_exp01.pt",
            "./models/asvspoof2019_la_recovery_exp01.pt",
            "models/asvspoof2019_la_resnet.pt",
            "./models/asvspoof2019_la_resnet.pt",
            "models/anti_spoofing_resnet.pt",
            "./models/anti_spoofing_resnet.pt"
        ])

        for c in candidates:
            abs_c = os.path.abspath(c)
            if os.path.exists(abs_c):
                return abs_c
        return None

    def _load_model(self):
        """Loads PyTorch model architecture and weights if present."""
        self.model = VoiceAntiSpoofingResNet()
        target_ckpt = self._resolve_checkpoint()
        if target_ckpt and os.path.exists(target_ckpt):
            try:
                ckpt = torch.load(target_ckpt, map_location="cpu")
                if isinstance(ckpt, dict) and "state_dict" in ckpt:
                    state_dict = ckpt["state_dict"]
                else:
                    state_dict = ckpt
                self.model.load_state_dict(state_dict)
                self.model_path = target_ckpt
            except Exception:
                pass
        self.model.eval()

    def predict(self, features: Union[ExtractedFeatures, np.ndarray]) -> AntiSpoofingResult:
        """
        Executes real PyTorch model forward pass on extracted Log-Mel Spectrogram features.
        Returns structured AntiSpoofingResult.
        """
        t0 = time.perf_counter()

        # Extract Log-Mel array from ExtractedFeatures or raw numpy input
        if isinstance(features, ExtractedFeatures):
            log_mel = features.log_mel_spectrogram
        elif isinstance(features, np.ndarray):
            log_mel = features
        else:
            log_mel = np.zeros((80, self.target_frames), dtype=np.float32)

        # Ensure 2D (80, T) array
        if log_mel.ndim == 1:
            log_mel = log_mel.reshape(1, -1)

        # 1. Standardize temporal frame dimension to target_frames (e.g. 300)
        n_mels, n_frames = log_mel.shape
        if n_frames < self.target_frames:
            pad_width = self.target_frames - n_frames
            log_mel_padded = np.pad(log_mel, ((0, 0), (0, pad_width)), mode="constant", constant_values=-23.0)
        elif n_frames > self.target_frames:
            start_frame = (n_frames - self.target_frames) // 2
            log_mel_padded = log_mel[:, start_frame:start_frame + self.target_frames]
        else:
            log_mel_padded = log_mel

        # 2. Z-score normalization per channel
        mean = np.mean(log_mel_padded)
        std = np.std(log_mel_padded) + 1e-7
        log_mel_norm = (log_mel_padded - mean) / std

        # 3. Reshape to PyTorch 4D tensor (batch_size=1, channel=1, mels=80, frames=300)
        input_tensor = torch.from_numpy(log_mel_norm).float().unsqueeze(0).unsqueeze(0)

        # 4. Neural Network Forward Pass
        if self.model is None:
            self._load_model()

        with torch.no_grad():
            logit = self.model(input_tensor)
            prob = torch.sigmoid(logit).item()

        t1 = time.perf_counter()
        elapsed_ms = round((t1 - t0) * 1000.0, 2)

        # Clamp score in range [0.0, 1.0]
        score = float(np.clip(prob, 0.0, 1.0))
        is_synth = score >= self.decision_threshold
        confidence = float(round(abs(score - 0.5) * 2.0, 4))

        return AntiSpoofingResult(
            synthetic_score=round(score, 4),
            is_synthetic=is_synth,
            confidence=confidence,
            model_version=self.model_version,
            inference_time_ms=elapsed_ms
        )

    def predict_synthetic_score(self, features: Union[ExtractedFeatures, np.ndarray]) -> float:
        """Convenience helper returning probability score float."""
        result = self.predict(features)
        return result.synthetic_score
