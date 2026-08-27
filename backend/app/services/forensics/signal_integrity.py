"""
Signal Integrity Module.

Analyzes clipping ratio, DC offset, peak-to-RMS ratio, crest factor, dynamic range,
and estimated noise floor to detect physical/digital distortion or amplifier overdrive.
"""

from typing import Dict, Any, List
import numpy as np

from app.services.forensics.types import EvidenceItem, EvidenceCategory, EvidenceDirection, ScientificStatus


def analyze_signal_integrity(signal: np.ndarray, sample_rate: int = 16000) -> List[EvidenceItem]:
    evidence: List[EvidenceItem] = []
    if len(signal) == 0:
        return evidence

    signal = np.squeeze(signal).astype(np.float32)
    n_samples = len(signal)

    # 1. Clipping Ratio (|x| >= 0.99)
    clipped_samples = np.sum(np.abs(signal) >= 0.99)
    clipping_ratio = float(clipped_samples / max(n_samples, 1))

    if clipping_ratio > 0.01:
        evidence.append(EvidenceItem(
            id="EV_INTEG_CLIPPING_SEVERE",
            category=EvidenceCategory.INTEGRITY.value,
            signal="clipping_ratio",
            value=round(clipping_ratio, 4),
            normalized_strength=min(1.0, clipping_ratio * 10.0),
            direction=EvidenceDirection.SUPPORTS_SPOOF.value,
            reliability=0.95,
            status=ScientificStatus.MEASURED.value,
            explanation=f"Severe digital waveform clipping detected ({round(clipping_ratio * 100, 2)}% of samples saturated)."
        ))

    # 2. DC Offset
    dc_offset = float(np.mean(signal))
    if abs(dc_offset) > 0.05:
        evidence.append(EvidenceItem(
            id="EV_INTEG_DC_OFFSET",
            category=EvidenceCategory.INTEGRITY.value,
            signal="dc_offset",
            value=round(dc_offset, 4),
            normalized_strength=min(1.0, abs(dc_offset) * 5.0),
            direction=EvidenceDirection.SUPPORTS_SPOOF.value,
            reliability=0.90,
            status=ScientificStatus.MEASURED.value,
            explanation=f"Significant DC bias offset detected ({round(dc_offset, 4)})."
        ))

    # 3. Peak-to-RMS Ratio & Crest Factor
    peak_val = float(np.max(np.abs(signal)))
    rms_val = float(np.sqrt(np.mean(signal ** 2))) + 1e-10
    crest_factor_linear = peak_val / rms_val
    crest_factor_db = float(20.0 * np.log10(crest_factor_linear + 1e-10))

    if crest_factor_db < 6.0:  # Abnormally low dynamic range (heavily dynamic-range compressed signal)
        evidence.append(EvidenceItem(
            id="EV_INTEG_CREST_FACTOR_LOW",
            category=EvidenceCategory.INTEGRITY.value,
            signal="crest_factor_db",
            value=round(crest_factor_db, 2),
            normalized_strength=0.72,
            direction=EvidenceDirection.SUPPORTS_SPOOF.value,
            reliability=0.88,
            status=ScientificStatus.MEASURED.value,
            explanation=f"Unusually low crest factor ({round(crest_factor_db, 2)} dB) indicating heavy dynamic range compression."
        ))

    # 4. Noise Floor Estimate (10th percentile frame energy)
    frame_len = 400
    hop_len = 160
    n_frames = max(1, (n_samples - frame_len) // hop_len + 1)
    frame_rms = [np.sqrt(np.mean(signal[i * hop_len:i * hop_len + frame_len] ** 2)) for i in range(n_frames)]
    noise_floor_rms = float(np.percentile(frame_rms, 10)) + 1e-10
    noise_floor_db = float(20.0 * np.log10(noise_floor_rms))

    if noise_floor_db > -30.0:  # High background noise
        evidence.append(EvidenceItem(
            id="EV_INTEG_NOISE_FLOOR_HIGH",
            category=EvidenceCategory.QUALITY.value,
            signal="noise_floor_db",
            value=round(noise_floor_db, 2),
            normalized_strength=0.60,
            direction=EvidenceDirection.INCONCLUSIVE.value,
            reliability=0.85,
            status=ScientificStatus.MEASURED.value,
            explanation=f"High background noise floor ({round(noise_floor_db, 1)} dB) degrades detection confidence."
        ))

    return evidence
