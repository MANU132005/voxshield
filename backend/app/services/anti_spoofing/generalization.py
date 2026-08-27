"""
Phase 3 Generalization & Spoofing Artifact Extractor.

Extracts physical and acoustic indicators of unseen voice spoofing attacks:
1. Phase Coherence Discontinuity (Vocoder phase synthesis anomalies)
2. Pitch Micro-Jitter & Fundamental Frequency ($F_0$) Stationarity (TTS over-regularity)
3. High-Frequency Vocoder Upsampling Band Artifacts (MelGAN, HiFi-GAN spectral cuts)
"""

import numpy as np
import scipy.signal
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class GeneralizationArtifacts:
    phase_coherence_score: float        # [0.0 - 1.0], higher indicates phase discontinuity (spoof indicator)
    pitch_jitter_score: float           # [0.0 - 1.0], lower indicates unnatural pitch rigidity (TTS indicator)
    hf_vocoder_artifact_score: float    # [0.0 - 1.0], higher indicates high-freq upsampling band anomaly
    generalization_risk_score: float    # [0.0 - 1.0], overall aggregated artifact risk score


class GeneralizationExtractor:
    def extract_artifacts(self, signal: np.ndarray, sample_rate: int = 16000) -> GeneralizationArtifacts:
        signal = signal.astype(np.float32)
        if len(signal) < sample_rate * 0.2:
            return GeneralizationArtifacts(0.0, 0.5, 0.0, 0.0)

        # 1. Phase Coherence Discontinuity
        n_fft = 512
        hop_length = 160
        stft = scipy.signal.stft(signal, fs=sample_rate, nperseg=n_fft, noverlap=n_fft - hop_length)[2]
        angles = np.angle(stft)
        phase_diff = np.diff(angles, axis=1)
        phase_var = float(np.mean(np.var(phase_diff, axis=0)))
        phase_coherence_score = float(np.clip(phase_var / 3.0, 0.0, 1.0))

        # 2. Pitch Micro-Jitter & F0 Stationarity
        autocorr = np.correlate(signal, signal, mode="full")
        autocorr = autocorr[len(autocorr)//2:]
        min_lag = int(sample_rate / 400) # Max F0 400Hz
        max_lag = int(sample_rate / 70)  # Min F0 70Hz

        if max_lag < len(autocorr):
            pitch_lags = autocorr[min_lag:max_lag]
            peak_val = np.max(pitch_lags) if len(pitch_lags) > 0 else 1.0
            mean_val = np.mean(pitch_lags) + 1e-10
            pitch_jitter_score = float(np.clip((peak_val / mean_val - 1.0) / 10.0, 0.0, 1.0))
        else:
            pitch_jitter_score = 0.5

        # 3. High-Frequency Vocoder Upsampling Band Artifacts (> 6 kHz)
        mag_spec = np.abs(stft)
        freqs = np.fft.rfftfreq(n_fft, d=1.0/sample_rate)
        hf_mask = freqs >= 6000.0
        lf_mask = (freqs >= 300.0) & (freqs < 4000.0)

        hf_energy = float(np.mean(mag_spec[hf_mask, :])) if np.any(hf_mask) else 1e-6
        lf_energy = float(np.mean(mag_spec[lf_mask, :])) if np.any(lf_mask) else 1.0

        hf_ratio = hf_energy / max(lf_energy, 1e-6)
        hf_vocoder_artifact_score = float(np.clip(hf_ratio * 5.0, 0.0, 1.0))

        # Aggregated generalization risk score
        gen_risk = float(np.clip(0.40 * phase_coherence_score + 0.30 * (1.0 - pitch_jitter_score) + 0.30 * hf_vocoder_artifact_score, 0.0, 1.0))

        return GeneralizationArtifacts(
            phase_coherence_score=round(phase_coherence_score, 4),
            pitch_jitter_score=round(pitch_jitter_score, 4),
            hf_vocoder_artifact_score=round(hf_vocoder_artifact_score, 4),
            generalization_risk_score=round(gen_risk, 4)
        )
