import os
import json
import tempfile
import scipy.io.wavfile
import numpy as np
import pytest

from scripts.audit_asvspoof import audit_asvspoof_dataset, parse_and_audit_split
from app.services.anti_spoofing.asvspoof_dataset import ASVspoofDataset


def test_missing_dataset_returns_blocked():
    result = audit_asvspoof_dataset(root_path="./non_existent_dataset_directory_xyz")
    assert result["dataset_found"] is False
    assert "BLOCKED" in result["status"]
    assert result["train"]["missing"] == "N/A"
    assert result["audio_integrity"]["min_duration_sec"] == "N/A"


def test_path_traversal_relative_rejected():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name
    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)
    protocol_file = os.path.join(dir_path, "ASVspoof2019.LA.cm.test.txt")

    lines = ["LA_0001 ../../etc/passwd - - bonafide\n"]
    with open(protocol_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir)
    assert len(dataset) == 1

    with pytest.raises(ValueError, match="Path traversal attempt detected"):
        _ = dataset[0]

    temp_dir.cleanup()


def test_path_traversal_absolute_outside_root_rejected():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name
    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)
    protocol_file = os.path.join(dir_path, "ASVspoof2019.LA.cm.test.txt")

    outside_abs_path = os.path.abspath("/Windows/System32/cmd.exe") if os.name == "nt" else "/etc/passwd"
    lines = [f"LA_0001 {outside_abs_path} - - bonafide\n"]
    with open(protocol_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir)
    assert len(dataset) == 1

    with pytest.raises(ValueError, match="Path traversal attempt detected"):
        _ = dataset[0]

    temp_dir.cleanup()


def test_duplicate_utterance_ids_detected():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name
    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)
    protocol_file = os.path.join(dir_path, "ASVspoof2019.LA.cm.test.txt")

    lines = [
        "LA_0001 LA_T_1000001 - - bonafide\n",
        "LA_0001 LA_T_1000001 - - bonafide\n"  # Duplicate utterance ID
    ]
    with open(protocol_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    stats = parse_and_audit_split(protocol_file, audio_dir, dir_path)
    assert stats["protocol_entries"] == 2
    assert len(stats["utterance_ids"]) == 1  # Deduplicated in set

    temp_dir.cleanup()


def test_speaker_overlap_detected():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name
    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)

    tr_file = os.path.join(dir_path, "train.txt")
    ev_file = os.path.join(dir_path, "eval.txt")

    with open(tr_file, "w", encoding="utf-8") as f:
        f.write("LA_0001 LA_T_1000001 - - bonafide\n")
    with open(ev_file, "w", encoding="utf-8") as f:
        f.write("LA_0001 LA_E_2000001 - A07 spoof\n")  # Same speaker LA_0001

    tr_stats = parse_and_audit_split(tr_file, audio_dir, dir_path)
    ev_stats = parse_and_audit_split(ev_file, audio_dir, dir_path)

    overlap = set(tr_stats["speaker_ids"]).intersection(set(ev_stats["speaker_ids"]))
    assert len(overlap) == 1
    assert "LA_0001" in overlap

    temp_dir.cleanup()


def test_duplicate_audio_path_resolution():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name
    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)

    # Create one flac file
    wav_path = os.path.join(audio_dir, "LA_T_1000001.wav")
    scipy.io.wavfile.write(wav_path, 16000, np.zeros(1600, dtype=np.int16))

    protocol_file = os.path.join(dir_path, "test.txt")
    with open(protocol_file, "w", encoding="utf-8") as f:
        f.write("LA_0001 LA_T_1000001 - - bonafide\n")

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir)
    resolved_1 = dataset._resolve_audio_path("LA_T_1000001")
    resolved_2 = dataset._resolve_audio_path("LA_T_1000001")

    assert resolved_1 == resolved_2
    assert resolved_1 is not None

    temp_dir.cleanup()


def test_malformed_protocol_line_handled_safely():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name
    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)
    protocol_file = os.path.join(dir_path, "test.txt")

    lines = [
        "LA_0001 LA_T_1000001 - bonafide\n",  # Only 4 columns (malformed)
        "LA_0002 LA_T_1000002 - - spoof\n"    # Valid 5 columns
    ]
    with open(protocol_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir)
    assert len(dataset) == 1
    assert dataset.malformed_lines_count == 1
    assert dataset.samples[0][1] == "LA_T_1000002"

    temp_dir.cleanup()


def test_invalid_label_key_rejected():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name
    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)
    protocol_file = os.path.join(dir_path, "test.txt")

    lines = [
        "LA_0001 LA_T_1000001 - - INVALID_KEY_LABEL\n",
        "LA_0002 LA_T_1000002 - - bonafide\n"
    ]
    with open(protocol_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir)
    assert len(dataset) == 1
    assert dataset.samples[0][1] == "LA_T_1000002"

    temp_dir.cleanup()


def test_missing_audio_file_reported_correctly():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name
    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)
    protocol_file = os.path.join(dir_path, "test.txt")

    with open(protocol_file, "w", encoding="utf-8") as f:
        f.write("LA_0001 NON_EXISTENT_AUDIO_FILE - - bonafide\n")

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir)
    assert len(dataset) == 1

    feature_tensor, label_tensor = dataset[0]
    assert dataset.missing_files_count == 1
    assert feature_tensor.shape == (1, 80, 300)

    temp_dir.cleanup()


def test_valid_mock_protocol_passes():
    temp_dir = tempfile.TemporaryDirectory()
    dir_path = temp_dir.name
    audio_dir = os.path.join(dir_path, "flac")
    os.makedirs(audio_dir, exist_ok=True)

    wav_path = os.path.join(audio_dir, "LA_T_1000001.wav")
    scipy.io.wavfile.write(wav_path, 16000, (np.sin(np.linspace(0, 1, 16000)) * 32767).astype(np.int16))

    protocol_file = os.path.join(dir_path, "test.txt")
    with open(protocol_file, "w", encoding="utf-8") as f:
        f.write("LA_0001 LA_T_1000001 - - bonafide\n")

    dataset = ASVspoofDataset(protocol_file=protocol_file, audio_dir=audio_dir)
    assert len(dataset) == 1
    feature_tensor, label_tensor = dataset[0]
    assert feature_tensor.shape == (1, 80, 300)
    assert label_tensor.item() == 0.0

    temp_dir.cleanup()


def test_json_audit_report_schema_validity():
    result = audit_asvspoof_dataset(root_path="./non_existent_path_xyz_schema_check")
    json_path = "reports/m9_dataset_audit.json"

    assert os.path.exists(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "dataset_found" in data
    assert "status" in data
    assert "security_analysis" in data
    assert "cross_split_leakage" in data or "leakage_analysis" in data
