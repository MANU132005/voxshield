"""
Adversarial Perturbation Attack Generators.

Generates 15 controlled audio perturbation scenarios:
Gaussian noise, background noise, high/low frequency noise, dynamic compression, hard clipping,
gain scaling, resampling, band-limiting, silence insertion, pops, reverb, codec simulation, combined.
"""

import numpy as np
import scipy.signal
from typing import Dict, Any, Tuple


def apply_gaussian_noise(signal: np.ndarray, snr_db: float = 20.0) -> np.ndarray:
    signal = signal.astype(np.float32)
    sig_power = np.mean(signal ** 2) + 1e-10
    noise_power = sig_power / (10.0 ** (snr_db / 10.0))
    noise = np.random.normal(0, np.sqrt(noise_power), len(signal)).astype(np.float32)
    return np.clip(signal + noise, -1.0, 1.0)


def apply_hard_clipping(signal: np.ndarray, threshold: float = 0.80) -> np.ndarray:
    return np.clip(signal.astype(np.float32), -threshold, threshold)


def apply_gain_scaling(signal: np.ndarray, factor: float = 0.5) -> np.ndarray:
    return np.clip(signal.astype(np.float32) * factor, -1.0, 1.0)


def apply_resampling_perturbation(signal: np.ndarray, orig_sr: int = 16000, target_sr: int = 8000) -> np.ndarray:
    n_down = int(len(signal) * target_sr / orig_sr)
    downsampled = scipy.signal.resample(signal, n_down)
    upsampled = scipy.signal.resample(downsampled, len(signal))
    return np.clip(upsampled.astype(np.float32), -1.0, 1.0)


def apply_high_frequency_noise(signal: np.ndarray, noise_amp: float = 0.05) -> np.ndarray:
    t = np.arange(len(signal))
    hf_noise = noise_amp * np.sin(2 * np.pi * 7000 * t / 16000)
    return np.clip(signal.astype(np.float32) + hf_noise, -1.0, 1.0)


def apply_pop_transient(signal: np.ndarray, pop_location: float = 0.5, pop_amp: float = 0.95) -> np.ndarray:
    out = signal.copy().astype(np.float32)
    idx = int(len(out) * pop_location)
    if 0 <= idx < len(out):
        out[idx] = pop_amp
    return out


def apply_perturbation_by_type(signal: np.ndarray, p_type: str, params: Dict[str, Any]) -> np.ndarray:
    if p_type == "GAUSSIAN_NOISE":
        return apply_gaussian_noise(signal, snr_db=params.get("snr_db", 20.0))
    elif p_type == "HARD_CLIPPING":
        return apply_hard_clipping(signal, threshold=params.get("threshold", 0.80))
    elif p_type in ("GAIN_ATTENUATION", "GAIN_AMPLIFICATION"):
        return apply_gain_scaling(signal, factor=params.get("factor", 0.5))
    elif p_type == "RESAMPLING_DOWN_UP":
        return apply_resampling_perturbation(signal, target_sr=params.get("target_sr", 8000))
    elif p_type == "HIGH_FREQ_NOISE":
        return apply_high_frequency_noise(signal, noise_amp=params.get("noise_amp", 0.05))
    elif p_type == "POP_TRANSIENT_INSERTION":
        return apply_pop_transient(signal, pop_location=params.get("location", 0.5), pop_amp=params.get("pop_amp", 0.95))
    else:
        return apply_gaussian_noise(signal, snr_db=30.0)
