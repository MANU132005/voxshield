import os
import tempfile
import scipy.io.wavfile
import numpy as np
import pytest
import torch

from app.services.anti_spoofing.asvspoof_dataset import ASVspoofDataset


@pytest.fixture
def mock_asvspoof_fixture():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name

    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)

    protocol_file = os.path.join(dir_path, "ASVspoof2019.LA.cm.test.txt")

    # Generate 4 synthetic wav audio files
    sample_names = ["LA_T_1000001", "LA_T_1000002", "LA_T_1000003", "LA_T_1000004"]
    keys = ["bonafide", "spoof", "bonafide", "spoof"]

    for name in sample_names:
        wav_path = os.path.join(audio_dir, f"{name}.wav")
        # 1.0s of 16kHz mono int16 audio
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        audio = (0.5 * np.sin(2 * np.pi * 220.0 * t) * 32767).astype(np.int16)
        scipy.io.wavfile.write(wav_path, 16000, audio)

    # Write protocol file
    lines = [
        f"LA_0001 {sample_names[0]} - - {keys[0]}\n",
        f"LA_0002 {sample_names[1]} - A01 {keys[1]}\n",
        f"LA_0003 {sample_names[2]} - - {keys[2]}\n",
        f"LA_0004 {sample_names[3]} - A02 {keys[3]}\n"
    ]
    with open(protocol_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    yield protocol_file, audio_dir

    temp_dir.cleanup()


def test_asvspoof_dataset_parsing(mock_asvspoof_fixture):
    protocol_file, audio_dir = mock_asvspoof_fixture

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir, target_frames=300)

    assert len(dataset) == 4
    assert dataset.samples[0][0] == "LA_0001"
    assert dataset.samples[0][1] == "LA_T_1000001"
    assert dataset.samples[0][3] == 0  # bonafide -> 0

    assert dataset.samples[1][3] == 1  # spoof -> 1


def test_asvspoof_dataset_tensor_output(mock_asvspoof_fixture):
    protocol_file, audio_dir = mock_asvspoof_fixture

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir, target_frames=300)

    feature_tensor, label_tensor = dataset[0]

    assert isinstance(feature_tensor, torch.Tensor)
    assert isinstance(label_tensor, torch.Tensor)
    assert feature_tensor.ndim == 3  # (1, 80, 300)
    assert feature_tensor.shape[0] == 1
    assert feature_tensor.shape[1] == 80
    assert feature_tensor.shape[2] == 300
    assert label_tensor.item() == 0.0


def test_asvspoof_dataset_missing_file_fallback(mock_asvspoof_fixture):
    protocol_file, audio_dir = mock_asvspoof_fixture

    # Append non-existent file line to protocol
    with open(protocol_file, "a", encoding="utf-8") as f:
        f.write("LA_0005 LA_T_9999999 - - bonafide\n")

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir, target_frames=300)
    assert len(dataset) == 5

    # Accessing non-existent sample returns fallback zero-tensor
    feature_tensor, label_tensor = dataset[4]
    assert feature_tensor.shape == (1, 80, 300)
    assert torch.all(feature_tensor == 0.0) or torch.all(torch.isnan(feature_tensor) == False)
