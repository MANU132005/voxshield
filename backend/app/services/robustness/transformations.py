"""
Controlled Audio Robustness Transformation Engine.

Applies 7 deterministic, non-destructive transformations:
Replay, Background Noise, Reverberation, Codec Compression, Clipping, Synthetic Variation, Controlled Perturbation.
"""

import numpy as np
import scipy.signal
from typing import Dict, Any, Tuple


def apply_replay_transformation(signal: np.ndarray, sample_rate: int = 16000, severity: str = "MEDIUM") -> np.ndarray:
    """Simulates acoustic replay spectral coloration via bandpass microphonic response filtering."""
    out = signal.astype(np.float32).copy()
    if len(out) == 0:
        return out

    # Determine cutoff frequencies based on severity
    low_cut = 300.0 if severity == "LOW" else (500.0 if severity == "MEDIUM" else 700.0)
    high_cut = 5000.0 if severity == "LOW" else (4000.0 if severity == "MEDIUM" else 3400.0)

    nyq = sample_rate / 2.0
    b, a = scipy.signal.butter(2, [low_cut / nyq, high_cut / nyq], btype="bandpass")
    filtered = scipy.signal.lfilter(b, a, out)
    return np.clip(filtered.astype(np.float32), -1.0, 1.0)


def apply_noise_transformation(signal: np.ndarray, snr_db: float = 20.0, seed: int = 42) -> np.ndarray:
    """Injects SNR-controlled background noise deterministically."""
    out = signal.astype(np.float32).copy()
    if len(out) == 0:
        return out

    np.random.seed(seed)
    sig_power = np.mean(out ** 2) + 1e-10
    noise_power = sig_power / (10.0 ** (snr_db / 10.0))
    noise = np.random.normal(0, np.sqrt(noise_power), len(out)).astype(np.float32)
    return np.clip(out + noise, -1.0, 1.0)


def apply_reverberation_transformation(signal: np.ndarray, sample_rate: int = 16000, decay: float = 0.5) -> np.ndarray:
    """Applies synthetic Room Impulse Response (RIR) reverberation decay convolution."""
    out = signal.astype(np.float32).copy()
    if len(out) == 0:
        return out

    # Generate synthetic exponential decay impulse response (~100ms)
    rir_len = int(sample_rate * 0.1)
    t = np.linspace(0, 0.1, rir_len)
    rir = np.exp(-t * 20.0 * decay) * np.sin(2 * np.pi * 500 * t)
    rir = rir / (np.sum(np.abs(rir)) + 1e-10)

    reverbed = scipy.signal.convolve(out, rir, mode="same")
    return np.clip(reverbed.astype(np.float32), -1.0, 1.0)


def apply_compression_transformation(signal: np.ndarray, sample_rate: int = 16000, target_sr: int = 8000) -> np.ndarray:
    """Simulates codec compression via downsampling/resampling degradation."""
    out = signal.astype(np.float32).copy()
    if len(out) == 0:
        return out

    n_down = int(len(out) * target_sr / sample_rate)
    if n_down <= 0:
        return out

    downsampled = scipy.signal.resample(out, n_down)
    upsampled = scipy.signal.resample(downsampled, len(out))
    return np.clip(upsampled.astype(np.float32), -1.0, 1.0)


def apply_clipping_transformation(signal: np.ndarray, threshold: float = 0.70) -> np.ndarray:
    """Applies amplitude hard clipping saturation."""
    out = signal.astype(np.float32).copy()
    if len(out) == 0:
        return out
    return np.clip(out, -threshold, threshold)


def apply_synthetic_variation_transformation(signal: np.ndarray, variation_type: str = "MODERATE_PITCH") -> Tuple[np.ndarray, str]:
    """Applies synthetic voice variation fixture transformation."""
    out = signal.astype(np.float32).copy()
    if len(out) == 0:
        return out, "INPUT_DATA_REQUIRED"

    # Apply pitch modulation simulation
    t = np.arange(len(out))
    mod = 0.05 * np.sin(2 * np.pi * 5.0 * t / 16000)
    out_mod = out * (1.0 + mod)
    return np.clip(out_mod.astype(np.float32), -1.0, 1.0), "FIXTURE_APPLIED"


def apply_controlled_perturbation_transformation(signal: np.ndarray, pert_amp: float = 0.02) -> np.ndarray:
    """Applies controlled low-level non-destructive additive perturbation."""
    out = signal.astype(np.float32).copy()
    if len(out) == 0:
        return out

    t = np.arange(len(out))
    pert = pert_amp * np.sin(2 * np.pi * 3500 * t / 16000)
    return np.clip(out + pert, -1.0, 1.0)
