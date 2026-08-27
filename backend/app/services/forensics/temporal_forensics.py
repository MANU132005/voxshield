"""
Temporal Forensics Module.

Analyzes zero crossing rate, frame energy variation, transient density, silence segmentation,
and envelope over-regularity to detect synthetic speech temporal anomalies.
"""

from typing import Dict, Any, List
import numpy as np

from app.services.forensics.types import EvidenceItem, EvidenceCategory, EvidenceDirection, ScientificStatus


def analyze_temporal_forensics(signal: np.ndarray, sample_rate: int = 16000) -> List[EvidenceItem]:
    evidence: List[EvidenceItem] = []
    if len(signal) == 0:
        return evidence

    signal = np.squeeze(signal).astype(np.float32)
    n_samples = len(signal)
    duration_sec = n_samples / sample_rate

    # 1. Zero Crossing Rate (ZCR)
    zero_crossings = np.sum(np.abs(np.diff(np.signbit(signal).astype(int))))
    zcr_rate = float(zero_crossings / max(n_samples, 1))

    if zcr_rate > 0.40:
        evidence.append(EvidenceItem(
            id="EV_TEMP_ZCR_HIGH",
            category=EvidenceCategory.TEMPORAL.value,
            signal="zero_crossing_rate",
            value=round(zcr_rate, 4),
            normalized_strength=0.70,
            direction=EvidenceDirection.SUPPORTS_SPOOF.value,
            reliability=0.82,
            status=ScientificStatus.INFERRED.value,
            explanation="Unusually high zero crossing rate (high-frequency noise or vocoder artifact)."
        ))

    # 2. Frame Energy Envelope Variation
    frame_len = 400
    hop_len = 160
    n_frames = max(1, (n_samples - frame_len) // hop_len + 1)

    frame_energies = []
    for i in range(n_frames):
        start = i * hop_len
        end = start + frame_len
        frame = signal[start:end]
        frame_energies.append(np.sum(frame ** 2))

    frame_energies = np.array(frame_energies)
    max_e = np.max(frame_energies) + 1e-10
    norm_energies = frame_energies / max_e
    energy_std = float(np.std(norm_energies))

    if energy_std < 0.05 and duration_sec >= 1.0:
        evidence.append(EvidenceItem(
            id="EV_TEMP_ENERGY_FLAT",
            category=EvidenceCategory.TEMPORAL.value,
            signal="energy_envelope_variation",
            value=round(energy_std, 4),
            normalized_strength=0.78,
            direction=EvidenceDirection.SUPPORTS_SPOOF.value,
            reliability=0.85,
            status=ScientificStatus.INFERRED.value,
            explanation="Abnormally static energy envelope across duration (indicates synthetic constant volume)."
        ))

    # 3. Silence Segmentation & Duration Check
    silent_frames = np.sum(norm_energies < 0.01)
    silence_ratio = float(silent_frames / max(n_frames, 1))

    if silence_ratio > 0.85:
        evidence.append(EvidenceItem(
            id="EV_TEMP_SILENCE_DOMINANT",
            category=EvidenceCategory.TEMPORAL.value,
            signal="silence_ratio",
            value=round(silence_ratio, 4),
            normalized_strength=0.60,
            direction=EvidenceDirection.INCONCLUSIVE.value,
            reliability=0.90,
            status=ScientificStatus.MEASURED.value,
            explanation="Audio signal consists predominantly of silence; reduced forensic reliability."
        ))

    return evidence
