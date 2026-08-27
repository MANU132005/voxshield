"""
Spectral Forensics Module.

Analyzes spectral stability, spectral flatness, spectral entropy, high-frequency energy ratio,
and frame-to-frame spectral variation to detect synthetic vocoder artifacts or acoustic anomalies.
"""

import math
from typing import Dict, Any, List
import numpy as np
import scipy.signal

from app.services.forensics.types import EvidenceItem, EvidenceCategory, EvidenceDirection, ScientificStatus


def analyze_spectral_forensics(signal: np.ndarray, sample_rate: int = 16000) -> List[EvidenceItem]:
    evidence: List[EvidenceItem] = []
    if len(signal) == 0:
        return evidence

    signal = np.squeeze(signal).astype(np.float32)

    # Compute single shared STFT for spectral forensics
    win_len = 400
    hop_len = 160
    n_fft = 512

    if len(signal) < win_len:
        signal = np.pad(signal, (0, win_len - len(signal)), mode="constant")

    freqs, _, Zxx = scipy.signal.stft(
        signal, fs=sample_rate, nperseg=win_len, noverlap=win_len - hop_len, nfft=n_fft, padded=True
    )
    mag_spec = np.abs(Zxx) + 1e-10
    power_spec = mag_spec ** 2
    n_bins, n_frames = mag_spec.shape

    # 1. SPECTRAL FLATNESS (Geometric Mean / Arithmetic Mean across frequency bins per frame)
    geom_mean = np.exp(np.mean(np.log(mag_spec), axis=0))
    arith_mean = np.mean(mag_spec, axis=0)
    flatness_per_frame = geom_mean / (arith_mean + 1e-10)
    mean_flatness = float(np.mean(flatness_per_frame))

    # Synthetic vocoder or buzz artifacts can cause unusual spectral flatness
    if mean_flatness < 0.03:
        evidence.append(EvidenceItem(
            id="EV_SPEC_FLAT_LOW",
            category=EvidenceCategory.SPECTRAL.value,
            signal="spectral_flatness",
            value=round(mean_flatness, 4),
            normalized_strength=0.75,
            direction=EvidenceDirection.SUPPORTS_SPOOF.value,
            reliability=0.85,
            status=ScientificStatus.INFERRED.value,
            explanation="Extremely low spectral flatness detected (indicates unnatural harmonic resonance)."
        ))
    elif mean_flatness > 0.45:
        evidence.append(EvidenceItem(
            id="EV_SPEC_FLAT_HIGH",
            category=EvidenceCategory.SPECTRAL.value,
            signal="spectral_flatness",
            value=round(mean_flatness, 4),
            normalized_strength=0.65,
            direction=EvidenceDirection.SUPPORTS_SPOOF.value,
            reliability=0.80,
            status=ScientificStatus.INFERRED.value,
            explanation="Unusually high spectral flatness detected (broadband noise / vocoder artifact)."
        ))
    else:
        evidence.append(EvidenceItem(
            id="EV_SPEC_FLAT_NORMAL",
            category=EvidenceCategory.SPECTRAL.value,
            signal="spectral_flatness",
            value=round(mean_flatness, 4),
            normalized_strength=0.20,
            direction=EvidenceDirection.SUPPORTS_GENUINE.value,
            reliability=0.90,
            status=ScientificStatus.INFERRED.value,
            explanation="Spectral flatness aligns with natural human speech formant distribution."
        ))

    # 2. SPECTRAL ENTROPY
    norm_power = power_spec / (np.sum(power_spec, axis=0, keepdims=True) + 1e-10)
    entropy_per_frame = -np.sum(norm_power * np.log2(norm_power + 1e-10), axis=0)
    max_entropy = math.log2(n_bins)
    norm_entropy_per_frame = entropy_per_frame / max_entropy
    mean_entropy = float(np.mean(norm_entropy_per_frame))

    if mean_entropy < 0.30:
        evidence.append(EvidenceItem(
            id="EV_SPEC_ENTROPY_LOW",
            category=EvidenceCategory.SPECTRAL.value,
            signal="spectral_entropy",
            value=round(mean_entropy, 4),
            normalized_strength=0.70,
            direction=EvidenceDirection.SUPPORTS_SPOOF.value,
            reliability=0.85,
            status=ScientificStatus.INFERRED.value,
            explanation="Abnormally low spectral entropy (indicates synthetic tone over-regularity)."
        ))

    # 3. SPECTRAL STATIONARITY & VARIATION
    if n_frames > 1:
        spectral_diffs = np.mean(np.abs(np.diff(mag_spec, axis=1)), axis=0)
        spec_variance = float(np.std(spectral_diffs))
        if spec_variance < 0.005:
            evidence.append(EvidenceItem(
                id="EV_SPEC_STATIONARY",
                category=EvidenceCategory.SPECTRAL.value,
                signal="spectral_stationarity",
                value=round(spec_variance, 6),
                normalized_strength=0.80,
                direction=EvidenceDirection.SUPPORTS_SPOOF.value,
                reliability=0.88,
                status=ScientificStatus.INFERRED.value,
                explanation="Unnatural spectral stationarity detected across time frames (vocoder frame repetition)."
            ))

    return evidence
