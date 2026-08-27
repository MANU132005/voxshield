"""
Phase 4/5 Live Audio Windowing System.

Slices raw audio signals into configurable, overlapping analysis windows with precise time offsets.
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from app.services.audio.processor import ProcessedAudio


@dataclass
class WindowConfig:
    window_duration_seconds: float = 1.0
    hop_duration_seconds: float = 0.5
    min_usable_duration_seconds: float = 0.5
    max_audio_duration_seconds: float = 30.0
    sample_rate: int = 16000


class LiveWindowingSystem:
    def __init__(self, config: WindowConfig = None):
        self.config = config or WindowConfig()

    def slice_windows(self, processed_audio: ProcessedAudio) -> List[Tuple[int, float, float, ProcessedAudio]]:
        signal = processed_audio.audio_signal
        sr = processed_audio.sample_rate

        duration = len(signal) / float(sr)
        if duration < self.config.min_usable_duration_seconds:
            return []

        # Enforce max duration limit
        max_samples = int(self.config.max_audio_duration_seconds * sr)
        if len(signal) > max_samples:
            signal = signal[:max_samples]

        win_samples = int(self.config.window_duration_seconds * sr)
        hop_samples = int(self.config.hop_duration_seconds * sr)

        if len(signal) <= win_samples:
            peak_amp = float(np.max(np.abs(signal))) if len(signal) > 0 else 0.0
            win_audio = ProcessedAudio(
                audio_signal=signal,
                sample_rate=sr,
                duration_seconds=round(len(signal) / float(sr), 4),
                channels=1,
                original_sample_rate=processed_audio.original_sample_rate,
                original_channels=processed_audio.original_channels,
                peak_amplitude=round(peak_amp, 5)
            )
            return [(0, 0.0, round(len(signal) / float(sr), 2), win_audio)]

        windows: List[Tuple[int, float, float, ProcessedAudio]] = []
        idx = 0
        start = 0

        while start + win_samples <= len(signal):
            chunk = signal[start:start + win_samples]
            start_sec = round(start / float(sr), 2)
            end_sec = round((start + win_samples) / float(sr), 2)
            peak_amp = float(np.max(np.abs(chunk))) if len(chunk) > 0 else 0.0

            win_audio = ProcessedAudio(
                audio_signal=chunk,
                sample_rate=sr,
                duration_seconds=self.config.window_duration_seconds,
                channels=1,
                original_sample_rate=processed_audio.original_sample_rate,
                original_channels=processed_audio.original_channels,
                peak_amplitude=round(peak_amp, 5)
            )

            windows.append((idx, start_sec, end_sec, win_audio))
            idx += 1
            start += hop_samples

        return windows
