"""
Audio Preprocessing & Acoustic Feature Extraction Module.

Developer 1 Responsibilities:
- Decode binary audio input into normalized float32 PCM array
- Convert multi-channel (stereo) audio to mono
- Resample audio to standard 16,000 Hz
- Peak-normalize signal to -1.0 dBFS
- Validate duration and signal quality
"""

import io
import math
import wave
from dataclasses import dataclass
from typing import Optional
import numpy as np
import scipy.io.wavfile
import scipy.signal

try:
    import soundfile as sf
except ImportError:
    sf = None


class AudioProcessingError(Exception):
    """Custom exception raised during audio validation, decoding, or preprocessing failure."""
    pass


@dataclass
class ProcessedAudio:
    audio_signal: np.ndarray  # 1D float32 numpy array, 16kHz mono, normalized to [-1.0, 1.0]
    sample_rate: int          # Target sample rate (16000 Hz)
    duration_seconds: float   # Audio duration in seconds
    channels: int             # Number of channels after preprocessing (1 for mono)
    original_sample_rate: int # Original input sample rate before resampling
    original_channels: int    # Original input channel count before mono conversion
    peak_amplitude: float     # Peak amplitude after normalization (-1.0 dBFS peak ~0.89125)


class AudioProcessor:
    def __init__(
        self,
        target_sample_rate: int = 16000,
        max_file_size_bytes: int = 15 * 1024 * 1024,  # 15 MB
        min_duration_seconds: float = 0.5,
        target_peak_dbfs: float = -1.0
    ):
        self.target_sample_rate = target_sample_rate
        self.max_file_size_bytes = max_file_size_bytes
        self.min_duration_seconds = min_duration_seconds
        self.target_peak_amplitude = 10.0 ** (target_peak_dbfs / 20.0)  # ~0.89125 for -1.0 dBFS

    def load_and_preprocess(self, audio_bytes: bytes, filename: Optional[str] = None) -> ProcessedAudio:
        """
        Full audio preprocessing pipeline:
        1. Validate file size and non-empty payload
        2. Decode raw audio bytes to float32 PCM array
        3. Convert multi-channel (stereo) to mono
        4. Resample to 16,000 Hz
        5. Peak-normalize to -1.0 dBFS
        6. Validate duration and signal presence
        """
        file_desc = f"'{filename}'" if filename else "Uploaded file"

        # 1. Payload validation
        if not audio_bytes or len(audio_bytes) == 0:
            raise AudioProcessingError("Uploaded audio file is empty.")

        if len(audio_bytes) > self.max_file_size_bytes:
            max_mb = self.max_file_size_bytes // (1024 * 1024)
            raise AudioProcessingError(f"{file_desc} exceeds maximum allowed size of {max_mb} MB.")

        # 2. Decode audio bytes
        signal, orig_sr = self._decode_audio(audio_bytes, file_desc)

        # 3. Channel handling (Stereo -> Mono)
        signal, orig_channels = self._to_mono(signal)

        # 4. Resample to 16,000 Hz
        if orig_sr != self.target_sample_rate:
            signal = self._resample(signal, orig_sr, self.target_sample_rate)

        # 5. Signal Quality & Duration Check (before normalization to detect true silence)
        peak_amp = float(np.max(np.abs(signal))) if len(signal) > 0 else 0.0
        if peak_amp < 1e-5:
            raise AudioProcessingError(f"{file_desc} contains no audible signal (complete silence).")

        duration = len(signal) / float(self.target_sample_rate)
        if duration < self.min_duration_seconds:
            raise AudioProcessingError(
                f"{file_desc} duration ({duration:.2f}s) is too short. Minimum duration required is {self.min_duration_seconds}s."
            )

        # 6. Peak Normalization to -1.0 dBFS
        signal = self._normalize_peak(signal, peak_amp)
        final_peak = float(np.max(np.abs(signal)))

        return ProcessedAudio(
            audio_signal=signal,
            sample_rate=self.target_sample_rate,
            duration_seconds=round(duration, 4),
            channels=1,
            original_sample_rate=orig_sr,
            original_channels=orig_channels,
            peak_amplitude=round(final_peak, 5)
        )

    def _decode_audio(self, audio_bytes: bytes, file_desc: str):
        """Attempts to decode audio bytes using soundfile, scipy.io.wavfile or stdlib wave."""
        if sf is not None:
            try:
                data, sr = sf.read(io.BytesIO(audio_bytes), dtype='float32')
                signal = self._convert_to_float32(data)
                return signal, sr
            except Exception:
                pass
        try:
            sr, raw_data = scipy.io.wavfile.read(io.BytesIO(audio_bytes))
            signal = self._convert_to_float32(raw_data)
            return signal, sr
        except Exception:
            pass

        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
                sr = wf.getframerate()
                n_frames = wf.getnframes()
                sample_width = wf.getsampwidth()
                n_channels = wf.getnchannels()
                raw_bytes = wf.readframes(n_frames)

                if sample_width == 2:
                    dtype = np.int16
                elif sample_width == 4:
                    dtype = np.int32
                elif sample_width == 1:
                    dtype = np.uint8
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")

                data = np.frombuffer(raw_bytes, dtype=dtype)
                if n_channels > 1:
                    data = data.reshape(-1, n_channels)
                signal = self._convert_to_float32(data)
                return signal, sr
        except Exception:
            pass

        raise AudioProcessingError(
            f"Could not decode audio file {file_desc}. Ensure it is a valid, uncorrupted WAV audio file."
        )

    def _convert_to_float32(self, data: np.ndarray) -> np.ndarray:
        """Converts integer PCM numpy array to float32 array in range [-1.0, 1.0]."""
        if data.dtype == np.float32 or data.dtype == np.float64:
            return data.astype(np.float32)
        elif data.dtype == np.int16:
            return (data.astype(np.float32) / 32768.0)
        elif data.dtype == np.int32:
            return (data.astype(np.float32) / 2147483648.0)
        elif data.dtype == np.uint8:
            return ((data.astype(np.float32) - 128.0) / 128.0)
        else:
            # Fallback scaling based on max abs
            max_val = np.max(np.abs(data))
            if max_val > 0:
                return (data.astype(np.float32) / max_val)
            return data.astype(np.float32)

    def _to_mono(self, signal: np.ndarray):
        """Converts multi-channel array to 1D mono array by channel averaging."""
        if signal.ndim == 1:
            return signal.astype(np.float32), 1
        elif signal.ndim == 2:
            # Shape is (samples, channels) or (channels, samples)
            if signal.shape[1] < signal.shape[0]:
                orig_channels = signal.shape[1]
                mono_signal = np.mean(signal, axis=1)
            else:
                orig_channels = signal.shape[0]
                mono_signal = np.mean(signal, axis=0)
            return mono_signal.astype(np.float32), orig_channels
        else:
            raise AudioProcessingError("Audio tensor has invalid dimension > 2.")

    def _resample(self, signal: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resamples signal to target_sr Hz using scipy.signal.resample_poly."""
        if len(signal) == 0:
            return signal
        g = math.gcd(orig_sr, target_sr)
        up = target_sr // g
        down = orig_sr // g
        try:
            resampled = scipy.signal.resample_poly(signal, up, down).astype(np.float32)
            return resampled
        except Exception:
            # Fallback interpolation if resample_poly fails
            num_samples = int(round(len(signal) * float(target_sr) / float(orig_sr)))
            orig_indices = np.linspace(0, len(signal) - 1, len(signal))
            new_indices = np.linspace(0, len(signal) - 1, num_samples)
            return np.interp(new_indices, orig_indices, signal).astype(np.float32)

    def _normalize_peak(self, signal: np.ndarray, current_peak: float) -> np.ndarray:
        """Normalizes peak absolute amplitude to target_peak_amplitude (-1.0 dBFS)."""
        if current_peak > 0:
            scale_factor = self.target_peak_amplitude / current_peak
            return signal * scale_factor
        return signal

    def extract_features(self, processed_audio: ProcessedAudio):
        """
        Extracts Log-Mel Spectrogram and LFCC features from ProcessedAudio object.
        """
        from app.services.audio.features import FeatureExtractor
        extractor = FeatureExtractor(sample_rate=self.target_sample_rate)
        return extractor.extract_features(processed_audio)
