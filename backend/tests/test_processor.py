import io
import math
import numpy as np
import pytest
import scipy.io.wavfile
from app.services.audio.processor import AudioProcessor, AudioProcessingError


def create_synthetic_wav_bytes(
    sample_rate: int = 16000,
    duration: float = 1.0,
    channels: int = 1,
    amplitude: float = 0.5,
    frequency: float = 440.0
) -> bytes:
    """Generates synthetic WAV audio bytes in memory for deterministic testing."""
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    mono_signal = amplitude * np.sin(2 * np.pi * frequency * t)

    if channels == 1:
        signal = mono_signal
    else:
        signal = np.column_stack([mono_signal] * channels)

    int16_signal = (signal * 32767).astype(np.int16)
    buf = io.BytesIO()
    scipy.io.wavfile.write(buf, sample_rate, int16_signal)
    return buf.getvalue()


@pytest.fixture
def processor():
    return AudioProcessor(target_sample_rate=16000, min_duration_seconds=0.5, target_peak_dbfs=-1.0)


def test_valid_wav_processing(processor):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    result = processor.load_and_preprocess(wav_bytes, filename="valid_16k.wav")

    assert result.sample_rate == 16000
    assert result.channels == 1
    assert math.isclose(result.duration_seconds, 1.0, abs_tol=0.05)
    assert result.original_sample_rate == 16000
    assert result.original_channels == 1
    assert result.audio_signal.ndim == 1
    assert len(result.audio_signal) == 16000


def test_stereo_to_mono_conversion(processor):
    stereo_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=2)
    result = processor.load_and_preprocess(stereo_bytes, filename="stereo.wav")

    assert result.original_channels == 2
    assert result.channels == 1
    assert result.audio_signal.ndim == 1
    assert len(result.audio_signal) == 16000


def test_non_16khz_to_16khz_resampling(processor):
    # 44.1 kHz input
    bytes_44k = create_synthetic_wav_bytes(sample_rate=44100, duration=1.0, channels=1)
    result_44k = processor.load_and_preprocess(bytes_44k, filename="44k.wav")

    assert result_44k.original_sample_rate == 44100
    assert result_44k.sample_rate == 16000
    assert len(result_44k.audio_signal) == 16000

    # 8 kHz input
    bytes_8k = create_synthetic_wav_bytes(sample_rate=8000, duration=1.0, channels=1)
    result_8k = processor.load_and_preprocess(bytes_8k, filename="8k.wav")

    assert result_8k.original_sample_rate == 8000
    assert result_8k.sample_rate == 16000
    assert len(result_8k.audio_signal) == 16000


def test_peak_amplitude_normalization(processor):
    # Unnormalized signal with low amplitude (0.1)
    low_amp_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1, amplitude=0.1)
    result = processor.load_and_preprocess(low_amp_bytes, filename="low_amp.wav")

    expected_target_peak = 10.0 ** (-1.0 / 20.0)  # ~0.89125
    actual_peak = float(np.max(np.abs(result.audio_signal)))

    assert math.isclose(actual_peak, expected_target_peak, abs_tol=1e-3)
    assert math.isclose(result.peak_amplitude, expected_target_peak, abs_tol=1e-3)


def test_empty_audio_rejection(processor):
    with pytest.raises(AudioProcessingError) as exc_info:
        processor.load_and_preprocess(b"", filename="empty.wav")
    assert "empty" in str(exc_info.value).lower()


def test_corrupted_audio_rejection(processor):
    corrupted_bytes = b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00BAD_HEADER_DATA"
    with pytest.raises(AudioProcessingError) as exc_info:
        processor.load_and_preprocess(corrupted_bytes, filename="corrupt.wav")
    assert "could not decode" in str(exc_info.value).lower() or "corrupted" in str(exc_info.value).lower()


def test_extremely_short_audio_rejection(processor):
    # 0.2 second audio (< 0.5s requirement)
    short_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=0.2, channels=1)
    with pytest.raises(AudioProcessingError) as exc_info:
        processor.load_and_preprocess(short_bytes, filename="short.wav")
    assert "too short" in str(exc_info.value).lower()


def test_silent_audio_rejection(processor):
    # Zero amplitude audio (complete silence)
    silent_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1, amplitude=0.0)
    with pytest.raises(AudioProcessingError) as exc_info:
        processor.load_and_preprocess(silent_bytes, filename="silent.wav")
    assert "silence" in str(exc_info.value).lower()


def test_output_channel_and_sample_rate_guarantees(processor):
    multi_channel_bytes = create_synthetic_wav_bytes(sample_rate=22050, duration=1.5, channels=2)
    result = processor.load_and_preprocess(multi_channel_bytes, filename="multi.wav")

    assert result.sample_rate == 16000
    assert result.channels == 1
    assert isinstance(result.audio_signal, np.ndarray)
    assert result.audio_signal.dtype == np.float32
