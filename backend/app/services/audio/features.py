"""
Audio Feature Extraction Layer.

Extracts deterministic Log-Mel Spectrogram and Linear Frequency Cepstral Coefficients (LFCC)
from standardized ProcessedAudio signals for future PyTorch anti-spoofing model inference.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple
import numpy as np
import scipy.signal
import scipy.fftpack
from app.services.audio.processor import ProcessedAudio, AudioProcessingError


@dataclass
class ExtractedFeatures:
    log_mel_spectrogram: np.ndarray  # Shape: (n_mels, n_frames), float32
    lfcc: np.ndarray                 # Shape: (n_lfcc, n_frames), float32
    sample_rate: int                 # 16000 Hz
    n_frames: int                    # Number of STFT time frames
    parameters: Dict[str, Any]       # Parameters used during extraction


class LogMelExtractor:
    """
    Log-Mel Spectrogram Extractor.
    Transforms 16kHz mono audio into Log-Mel Spectrogram using STFT and triangular Mel filterbank.
    """
    def __init__(
        self,
        sample_rate: int = 16000,
        n_fft: int = 512,
        win_length: int = 400,   # 25ms at 16kHz
        hop_length: int = 160,   # 10ms at 16kHz
        n_mels: int = 80,
        f_min: float = 0.0,
        f_max: float = 8000.0,
        eps: float = 1e-10
    ):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.f_min = f_min
        self.f_max = f_max
        self.eps = eps
        self.mel_filterbank = self._create_mel_filterbank()

    def _hz_to_mel(self, hz: float) -> float:
        return 2595.0 * np.log10(1.0 + hz / 700.0)

    def _mel_to_hz(self, mel: float) -> float:
        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

    def _create_mel_filterbank(self) -> np.ndarray:
        """Constructs triangular Mel filterbank matrix of shape (n_mels, n_fft // 2 + 1)."""
        num_fft_bins = self.n_fft // 2 + 1
        mel_min = self._hz_to_mel(self.f_min)
        mel_max = self._hz_to_mel(self.f_max)

        mel_points = np.linspace(mel_min, mel_max, self.n_mels + 2)
        hz_points = np.array([self._mel_to_hz(m) for m in mel_points])
        bin_points = np.floor((self.n_fft + 1) * hz_points / self.sample_rate).astype(int)

        fb = np.zeros((self.n_mels, num_fft_bins), dtype=np.float32)
        for m in range(1, self.n_mels + 1):
            f_m_minus = bin_points[m - 1]
            f_m = bin_points[m]
            f_m_plus = bin_points[m + 1]

            if f_m > f_m_minus:
                for k in range(f_m_minus, f_m):
                    if k < num_fft_bins:
                        fb[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
            if f_m_plus > f_m:
                for k in range(f_m, f_m_plus):
                    if k < num_fft_bins:
                        fb[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

        return fb

    def extract(self, signal: np.ndarray) -> np.ndarray:
        """
        Computes Log-Mel Spectrogram from 1D float32 audio signal.
        Returns 2D float32 array of shape (n_mels, n_frames).
        """
        if len(signal) < self.win_length:
            pad_len = self.win_length - len(signal)
            signal = np.pad(signal, (0, pad_len), mode="constant")

        # Compute STFT magnitude power spectrogram
        _, _, Zxx = scipy.signal.stft(
            signal,
            fs=self.sample_rate,
            nperseg=self.win_length,
            noverlap=self.win_length - self.hop_length,
            nfft=self.n_fft,
            padded=True
        )
        power_spec = (np.abs(Zxx) ** 2).astype(np.float32)

        # Apply Mel filterbank
        mel_spec = np.dot(self.mel_filterbank, power_spec)

        # Compute log scale with epsilon guard
        log_mel = np.log(np.maximum(mel_spec, self.eps)).astype(np.float32)

        # Guarantee finite numerical values (no NaN / Inf)
        log_mel = np.nan_to_num(log_mel, nan=-23.0, posinf=0.0, neginf=-23.0).astype(np.float32)
        return log_mel


class LFCCExtractor:
    """
    LFCC (Linear Frequency Cepstral Coefficients) Extractor.
    Transforms 16kHz mono audio into LFCC coefficients using linear triangular filterbank & DCT-II.
    """
    def __init__(
        self,
        sample_rate: int = 16000,
        n_fft: int = 512,
        win_length: int = 400,   # 25ms
        hop_length: int = 160,   # 10ms
        n_filters: int = 60,
        n_lfcc: int = 20,
        f_min: float = 0.0,
        f_max: float = 8000.0,
        eps: float = 1e-10
    ):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length
        self.n_filters = n_filters
        self.n_lfcc = n_lfcc
        self.f_min = f_min
        self.f_max = f_max
        self.eps = eps
        self.linear_filterbank = self._create_linear_filterbank()

    def _create_linear_filterbank(self) -> np.ndarray:
        """Constructs triangular linear filterbank matrix of shape (n_filters, n_fft // 2 + 1)."""
        num_fft_bins = self.n_fft // 2 + 1
        hz_points = np.linspace(self.f_min, self.f_max, self.n_filters + 2)
        bin_points = np.floor((self.n_fft + 1) * hz_points / self.sample_rate).astype(int)

        fb = np.zeros((self.n_filters, num_fft_bins), dtype=np.float32)
        for m in range(1, self.n_filters + 1):
            f_m_minus = bin_points[m - 1]
            f_m = bin_points[m]
            f_m_plus = bin_points[m + 1]

            if f_m > f_m_minus:
                for k in range(f_m_minus, f_m):
                    if k < num_fft_bins:
                        fb[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
            if f_m_plus > f_m:
                for k in range(f_m, f_m_plus):
                    if k < num_fft_bins:
                        fb[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

        return fb

    def extract(self, signal: np.ndarray) -> np.ndarray:
        """
        Computes LFCC coefficients from 1D float32 audio signal.
        Returns 2D float32 array of shape (n_lfcc, n_frames).
        """
        if len(signal) < self.win_length:
            pad_len = self.win_length - len(signal)
            signal = np.pad(signal, (0, pad_len), mode="constant")

        # Compute STFT magnitude power spectrogram
        _, _, Zxx = scipy.signal.stft(
            signal,
            fs=self.sample_rate,
            nperseg=self.win_length,
            noverlap=self.win_length - self.hop_length,
            nfft=self.n_fft,
            padded=True
        )
        power_spec = (np.abs(Zxx) ** 2).astype(np.float32)

        # Apply Linear filterbank
        lin_spec = np.dot(self.linear_filterbank, power_spec)

        # Compute log scale
        log_lin = np.log(np.maximum(lin_spec, self.eps)).astype(np.float32)

        # Apply Discrete Cosine Transform (DCT-II) along filter axis
        dct_coeffs = scipy.fftpack.dct(log_lin, type=2, axis=0, norm="ortho")
        lfcc = dct_coeffs[:self.n_lfcc, :].astype(np.float32)

        # Guarantee finite numerical values (no NaN / Inf)
        lfcc = np.nan_to_num(lfcc, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
        return lfcc


class FeatureExtractor:
    """
    Unified Feature Extraction Coordinator.
    Consumes ProcessedAudio and extracts Log-Mel Spectrogram and LFCC features.
    """
    def __init__(
        self,
        sample_rate: int = 16000,
        n_fft: int = 512,
        win_length: int = 400,
        hop_length: int = 160,
        n_mels: int = 80,
        n_filters: int = 60,
        n_lfcc: int = 20
    ):
        self.sample_rate = sample_rate
        self.log_mel_extractor = LogMelExtractor(
            sample_rate=sample_rate,
            n_fft=n_fft,
            win_length=win_length,
            hop_length=hop_length,
            n_mels=n_mels
        )
        self.lfcc_extractor = LFCCExtractor(
            sample_rate=sample_rate,
            n_fft=n_fft,
            win_length=win_length,
            hop_length=hop_length,
            n_filters=n_filters,
            n_lfcc=n_lfcc
        )

    def extract_features(self, processed_audio: ProcessedAudio) -> ExtractedFeatures:
        """
        Extracts Log-Mel Spectrogram and LFCC features from ProcessedAudio object.
        Returns ExtractedFeatures dataclass with float32 arrays.
        """
        if processed_audio is None or processed_audio.audio_signal is None:
            raise AudioProcessingError("Cannot extract features from invalid or null ProcessedAudio.")

        log_mel = self.log_mel_extractor.extract(processed_audio.audio_signal)
        lfcc = self.lfcc_extractor.extract(processed_audio.audio_signal)

        n_frames = log_mel.shape[1]

        return ExtractedFeatures(
            log_mel_spectrogram=log_mel,
            lfcc=lfcc,
            sample_rate=self.sample_rate,
            n_frames=n_frames,
            parameters={
                "sample_rate": self.sample_rate,
                "n_fft": self.log_mel_extractor.n_fft,
                "win_length": self.log_mel_extractor.win_length,
                "hop_length": self.log_mel_extractor.hop_length,
                "n_mels": self.log_mel_extractor.n_mels,
                "n_filters": self.lfcc_extractor.n_filters,
                "n_lfcc": self.lfcc_extractor.n_lfcc,
            }
        )
