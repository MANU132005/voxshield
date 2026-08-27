"""
DSP-Based Acoustic Replay Attack Detection Engine.

Analyzes acoustic cues, spectral roll-off, high-frequency attenuation, clipping saturation,
noise floor, and transient pop anomalies to compute an acoustic replay likelihood indicator score.
Uses a single shared STFT computation for maximum CPU performance efficiency.
"""

import time
import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
import numpy as np
import scipy.signal

from app.services.audio.processor import ProcessedAudio, AudioProcessingError


@dataclass
class ReplayFeatures:
    # Spectral Features (calculated from single shared STFT)
    spectral_flux_mean: float           # Mean frame-to-frame spectral change
    spectral_flux_std: float            # Standard deviation of spectral flux
    spectral_centroid_hz: float         # Spectral center of mass in Hz
    spectral_rolloff_hz: float          # 85% energy frequency bound in Hz
    spectral_bandwidth_hz: float        # Spectral spread around centroid in Hz
    high_freq_energy_ratio: float       # Ratio of energy > 6000 Hz to total energy
    high_freq_attenuation_ratio: float  # Ratio of energy 4kHz-8kHz to energy 0-4kHz

    # Signal Integrity & Time-Domain Features
    rms_energy: float                   # Root Mean Square energy
    peak_amplitude: float               # Peak absolute amplitude
    peak_to_rms_ratio: float            # Crest factor
    clipping_ratio: float               # Percentage of samples near clipping threshold (|x| >= 0.99)
    zero_crossing_rate: float           # Normalized zero-crossing count
    dynamic_range_db: float             # Peak-to-noise floor dynamic range in dB

    # Acoustic / Replay Indicators
    transient_density: float            # Count of energy pop/transient spikes per second
    estimated_noise_floor_db: float     # 10th percentile background noise floor in dB
    signal_to_noise_ratio_db: float     # Estimated SNR in dB
    temporal_energy_decay_rate: float   # Energy decay statistic across time frames


@dataclass
class ReplayDetectionResult:
    replay_score: float                 # Acoustic replay indicator score [0.0 - 1.0]
    confidence: float                   # Evidence confidence magnitude [0.0 - 1.0]
    risk_level: str                     # "LOW", "MEDIUM", "HIGH"
    triggered_indicators: List[str]     # Human-readable evidence reasons
    feature_summary: Dict[str, float]   # Key numerical DSP measurements
    processing_time_ms: float           # CPU processing duration in milliseconds
    detector_version: str               # "dsp_replay_v1.0"


class ReplayDetector:
    """
    DSP-Based Acoustic Replay Attack Detector.

    Evaluates acoustic characteristics associated with re-recording speech through
    physical loudspeakers and microphones (band-limiting, high-freq attenuation,
    non-linear saturation clipping, transient pop anomalies, and room noise floor).
    """
    def __init__(
        self,
        sample_rate: int = 16000,
        n_fft: int = 512,
        win_length: int = 400,     # 25ms
        hop_length: int = 160,     # 10ms
        high_freq_cutoff_hz: float = 6000.0,
        clipping_threshold: float = 0.99,
        detector_version: str = "dsp_replay_v1.0"
    ):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length
        self.high_freq_cutoff_hz = high_freq_cutoff_hz
        self.clipping_threshold = clipping_threshold
        self.detector_version = detector_version

    def extract_replay_features(self, signal: np.ndarray) -> ReplayFeatures:
        """
        Extracts spectral, time-domain, and acoustic replay features using a SINGLE SHARED STFT.
        Guarantees finite, non-NaN numerical outputs.
        """
        if len(signal) == 0:
            signal = np.zeros(self.win_length, dtype=np.float32)

        # Ensure 1D float32 array
        signal = np.squeeze(signal).astype(np.float32)
        if signal.ndim == 0:
            signal = np.zeros(self.win_length, dtype=np.float32)

        # 1. TIME-DOMAIN & SIGNAL INTEGRITY FEATURES
        abs_signal = np.abs(signal)
        peak_amp = float(np.max(abs_signal)) if len(abs_signal) > 0 else 0.0
        mean_sq = float(np.mean(signal ** 2)) if len(signal) > 0 else 0.0
        rms_val = float(math.sqrt(max(mean_sq, 1e-10)))
        peak_to_rms = float(peak_amp / (rms_val + 1e-7))

        # Clipping Ratio (% of samples >= clipping_threshold)
        clipped_count = int(np.sum(abs_signal >= self.clipping_threshold))
        clipping_ratio = float(clipped_count / max(len(signal), 1))

        # Zero Crossing Rate
        if len(signal) > 1:
            zero_crossings = np.sum(np.diff(np.signbit(signal)))
            zcr = float(zero_crossings / (len(signal) - 1))
        else:
            zcr = 0.0

        # 2. SINGLE SHARED STFT CALCULATION
        if len(signal) < self.win_length:
            signal_padded = np.pad(signal, (0, self.win_length - len(signal)), mode="constant")
        else:
            signal_padded = signal

        freqs, _, Zxx = scipy.signal.stft(
            signal_padded,
            fs=self.sample_rate,
            nperseg=self.win_length,
            noverlap=self.win_length - self.hop_length,
            nfft=self.n_fft,
            padded=True
        )

        mag_spec = np.abs(Zxx).astype(np.float32)       # Shape: (freq_bins, n_frames)
        power_spec = (mag_spec ** 2).astype(np.float32) # Shape: (freq_bins, n_frames)

        n_bins, n_frames = mag_spec.shape

        # A. Spectral Flux (Frame-to-frame magnitude difference)
        if n_frames > 1:
            flux_frames = np.sqrt(np.sum((mag_spec[:, 1:] - mag_spec[:, :-1]) ** 2, axis=0))
            flux_mean = float(np.mean(flux_frames))
            flux_std = float(np.std(flux_frames))
        else:
            flux_mean = 0.0
            flux_std = 0.0

        # B. Spectral Centroid
        frame_energies = np.sum(power_spec, axis=0) + 1e-10
        centroids = np.sum(freqs[:, np.newaxis] * power_spec, axis=0) / frame_energies
        spectral_centroid = float(np.mean(centroids))

        # C. Spectral Rolloff (85% Energy Frequency Bound)
        cum_power = np.cumsum(power_spec, axis=0)
        total_power = cum_power[-1, :] + 1e-10
        rolloff_bins = np.argmax(cum_power >= 0.85 * total_power, axis=0)
        rolloff_freqs = freqs[rolloff_bins]
        spectral_rolloff = float(np.mean(rolloff_freqs))

        # D. Spectral Bandwidth (Spread around Centroid)
        freq_diff_sq = (freqs[:, np.newaxis] - centroids[np.newaxis, :]) ** 2
        bandwidths = np.sqrt(np.sum(freq_diff_sq * power_spec, axis=0) / frame_energies)
        spectral_bandwidth = float(np.mean(bandwidths))

        # E. High-Frequency Energy Ratio (> 6000 Hz)
        hf_mask = freqs >= self.high_freq_cutoff_hz
        total_spectral_energy = np.sum(power_spec) + 1e-10
        hf_energy = np.sum(power_spec[hf_mask, :])
        hf_energy_ratio = float(hf_energy / total_spectral_energy)

        # F. High-Frequency Attenuation Ratio (4kHz-8kHz energy vs 0-4kHz energy)
        band_4k_8k = (freqs >= 4000.0) & (freqs <= 8000.0)
        band_0_4k = (freqs >= 0.0) & (freqs < 4000.0)
        e_4k_8k = np.sum(power_spec[band_4k_8k, :]) + 1e-10
        e_0_4k = np.sum(power_spec[band_0_4k, :]) + 1e-10
        hf_attenuation_ratio = float(e_4k_8k / e_0_4k)

        # 3. NOISE FLOOR & ACOUSTIC INDICATORS
        # Frame RMS in dB
        frame_rms = np.sqrt(np.mean(power_spec, axis=0)) + 1e-10
        frame_db = 20.0 * np.log10(np.maximum(frame_rms, 1e-10))

        # 10th percentile for noise floor
        est_noise_floor_db = float(np.percentile(frame_db, 10))
        peak_frame_db = float(np.max(frame_db))
        snr_db = max(peak_frame_db - est_noise_floor_db, 0.0)
        dynamic_range_db = float(20.0 * np.log10(max(peak_amp, 1e-5) / max(10 ** (est_noise_floor_db / 20.0), 1e-5)))

        # Transient / Pop Density (Count of 10ms frame energy spikes > 4x local median)
        duration_sec = max(len(signal) / float(self.sample_rate), 0.1)
        med_energy = np.median(frame_energies) + 1e-10
        transient_spikes = int(np.sum(frame_energies > 4.0 * med_energy))
        transient_density = float(transient_spikes / duration_sec)

        # Temporal Energy Decay Rate
        if n_frames > 1:
            decay_diffs = np.maximum(frame_energies[:-1] - frame_energies[1:], 0.0)
            decay_rate = float(np.mean(decay_diffs) / med_energy)
        else:
            decay_rate = 0.0

        return ReplayFeatures(
            spectral_flux_mean=float(np.nan_to_num(flux_mean, nan=0.0)),
            spectral_flux_std=float(np.nan_to_num(flux_std, nan=0.0)),
            spectral_centroid_hz=float(np.nan_to_num(spectral_centroid, nan=0.0)),
            spectral_rolloff_hz=float(np.nan_to_num(spectral_rolloff, nan=0.0)),
            spectral_bandwidth_hz=float(np.nan_to_num(spectral_bandwidth, nan=0.0)),
            high_freq_energy_ratio=float(np.clip(np.nan_to_num(hf_energy_ratio, nan=0.0), 0.0, 1.0)),
            high_freq_attenuation_ratio=float(np.nan_to_num(hf_attenuation_ratio, nan=0.0)),
            rms_energy=float(np.nan_to_num(rms_val, nan=0.0)),
            peak_amplitude=float(np.nan_to_num(peak_amp, nan=0.0)),
            peak_to_rms_ratio=float(np.nan_to_num(peak_to_rms, nan=0.0)),
            clipping_ratio=float(np.clip(np.nan_to_num(clipping_ratio, nan=0.0), 0.0, 1.0)),
            zero_crossing_rate=float(np.clip(np.nan_to_num(zcr, nan=0.0), 0.0, 1.0)),
            dynamic_range_db=float(np.nan_to_num(dynamic_range_db, nan=0.0)),
            transient_density=float(np.nan_to_num(transient_density, nan=0.0)),
            estimated_noise_floor_db=float(np.nan_to_num(est_noise_floor_db, nan=-80.0)),
            signal_to_noise_ratio_db=float(np.nan_to_num(snr_db, nan=0.0)),
            temporal_energy_decay_rate=float(np.nan_to_num(decay_rate, nan=0.0))
        )

    def analyze_replay_detailed(self, audio: Union[ProcessedAudio, np.ndarray]) -> ReplayDetectionResult:
        """
        Executes complete DSP acoustic replay feature extraction and evidence scoring engine.
        Returns detailed ReplayDetectionResult.
        """
        t0 = time.perf_counter()

        if isinstance(audio, ProcessedAudio):
            signal = audio.audio_signal
        elif isinstance(audio, np.ndarray):
            signal = audio
        else:
            signal = np.zeros(self.win_length, dtype=np.float32)

        # 1. Extract DSP Features using shared STFT
        feats = self.extract_replay_features(signal)

        # 2. EVIDENCE EVALUATION & REASON GENERATION
        triggered_reasons: List[str] = []
        score_components: List[float] = []

        # Feature A: High-Frequency Attenuation Indicator (Speaker band-limiting < 4kHz)
        # Replayed audio through small mobile speakers suffers heavy high-frequency loss
        if feats.high_freq_attenuation_ratio < 0.08:
            score_components.append(0.35)
            triggered_reasons.append("High-frequency spectral attenuation detected (indicates speaker output band-limiting)")
        elif feats.high_freq_attenuation_ratio < 0.18:
            score_components.append(0.18)

        # Feature B: Signal Saturation Clipping (Amplifier / Mic saturation)
        if feats.clipping_ratio > 0.01:
            score_components.append(0.30)
            triggered_reasons.append("Elevated signal clipping ratio detected (indicates amplifier or microphone saturation)")
        elif feats.clipping_ratio > 0.001:
            score_components.append(0.15)

        # Feature C: Transient / Pop Anomalies
        if feats.transient_density > 12.0:
            score_components.append(0.20)
            triggered_reasons.append("Transient energy discontinuities / pop anomalies detected")
        elif feats.transient_density > 6.0:
            score_components.append(0.10)

        # Feature D: Elevated Acoustic Noise Floor (Re-recording ambient room noise)
        if feats.estimated_noise_floor_db > -35.0:
            score_components.append(0.15)
            triggered_reasons.append("Elevated acoustic noise floor indicator")

        # Feature E: Spectral Flux Variance Anomaly
        if feats.spectral_flux_std > 8.0:
            score_components.append(0.10)
            triggered_reasons.append("Unusual spectral flux variation across time frames")

        # 3. WEIGHTED SCORE CALCULATION & RISK LEVEL ASSIGNMENT
        if score_components:
            raw_score = sum(score_components)
        else:
            raw_score = 0.05  # Baseline minimal score

        replay_score = float(np.clip(raw_score, 0.0, 1.0))
        confidence = float(round(abs(replay_score - 0.5) * 2.0, 4))

        if replay_score >= 0.65:
            risk_level = "HIGH"
        elif replay_score >= 0.35:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        t1 = time.perf_counter()
        elapsed_ms = round((t1 - t0) * 1000.0, 2)

        return ReplayDetectionResult(
            replay_score=round(replay_score, 4),
            confidence=confidence,
            risk_level=risk_level,
            triggered_indicators=triggered_reasons,
            feature_summary={
                "spectral_centroid_hz": round(feats.spectral_centroid_hz, 1),
                "spectral_rolloff_hz": round(feats.spectral_rolloff_hz, 1),
                "high_freq_energy_ratio": round(feats.high_freq_energy_ratio, 4),
                "clipping_ratio": round(feats.clipping_ratio, 5),
                "rms_energy": round(feats.rms_energy, 4),
                "transient_density": round(feats.transient_density, 2),
                "estimated_noise_floor_db": round(feats.estimated_noise_floor_db, 1)
            },
            processing_time_ms=elapsed_ms,
            detector_version=self.detector_version
        )

    def analyze_replay(self, audio: Union[ProcessedAudio, np.ndarray]) -> float:
        """
        Convenience helper method returning acoustic replay score float [0.0 - 1.0].
        Maintains backward compatibility with existing API routes.
        """
        result = self.analyze_replay_detailed(audio)
        return result.replay_score
