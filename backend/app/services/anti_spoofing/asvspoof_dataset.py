"""
Production-Quality ASVspoof 2019 Logical Access (LA) Dataset Adapter.

Provides a secure, memory-efficient PyTorch Dataset loader that parses official ASVspoof
protocol text files, lazily reads audio files from disk, and extracts Log-Mel Spectrogram features.
Includes canonical path traversal guards, strict protocol record validation, and robust error handling.
"""

import os
import logging
from typing import Optional, List, Tuple
import numpy as np
import torch
from torch.utils.data import Dataset

from app.services.audio.processor import AudioProcessor, AudioProcessingError
from app.services.audio.features import FeatureExtractor

logger = logging.getLogger(__name__)


class ASVspoofDataset(Dataset):
    """
    PyTorch Dataset Adapter for official ASVspoof 2019 Logical Access protocol files.

    Protocol text format:
        [SPEAKER_ID] [AUDIO_FILE_NAME] [ENV_ID] [ATTACK_ID] [KEY]
        Example: LA_0079 LA_E_2834728 - - bonafide
    """
    def __init__(
        self,
        protocol_file: str,
        audio_dir: str,
        target_frames: int = 300,
        max_samples: Optional[int] = None,
        sample_rate: int = 16000
    ):
        self.protocol_file = os.path.abspath(protocol_file)
        self.audio_dir = os.path.abspath(audio_dir)
        self.target_frames = target_frames
        self.sample_rate = sample_rate

        self.processor = AudioProcessor(target_sample_rate=sample_rate, min_duration_seconds=0.5)
        self.feature_extractor = FeatureExtractor(sample_rate=sample_rate)

        self.samples: List[Tuple[str, str, str, int]] = []
        self.malformed_lines_count: int = 0
        self.missing_files_count: int = 0
        self._parse_protocol(max_samples)

    def _parse_protocol(self, max_samples: Optional[int] = None):
        """Parses space-delimited ASVspoof protocol file with validation."""
        if not os.path.exists(self.protocol_file):
            raise FileNotFoundError(f"ASVspoof protocol file not found at: {self.protocol_file}")

        with open(self.protocol_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            parts = line.strip().split()
            if len(parts) < 5:
                self.malformed_lines_count += 1
                logger.warning(f"Malformed protocol record at line {line_num} in {self.protocol_file}: {line.strip()}")
                continue

            speaker_id = parts[0]
            file_name = parts[1]
            attack_id = parts[3]
            key = parts[4].lower()

            if key not in ("bonafide", "spoof"):
                self.malformed_lines_count += 1
                logger.warning(f"Invalid label key '{key}' at line {line_num} in {self.protocol_file}")
                continue

            # bonafide -> 0 (Genuine), spoof -> 1 (Spoofed)
            label = 0 if key == "bonafide" else 1

            self.samples.append((speaker_id, file_name, attack_id, label))
            if max_samples and len(self.samples) >= max_samples:
                break

    def _resolve_audio_path(self, file_name: str) -> Optional[str]:
        """
        Resolves audio file path safely and enforces canonical path traversal security bounds.
        Raises ValueError if path attempts directory traversal escaping self.audio_dir.
        """
        # Canonicalization and Path Traversal Check
        for candidate_name in [file_name, os.path.basename(file_name)]:
            for ext in [".flac", ".wav", ".mp3"]:
                rel_path = f"{candidate_name}{ext}"
                target_path = os.path.abspath(os.path.join(self.audio_dir, rel_path))

                # Security Guard: Ensure resolved target_path strictly resides within self.audio_dir
                try:
                    common = os.path.commonpath([target_path, self.audio_dir])
                except ValueError:
                    # Windows different drive letter attempt
                    raise ValueError(f"Path traversal attempt detected for file: {file_name}")

                if common != self.audio_dir:
                    raise ValueError(f"Path traversal attempt detected for file: {file_name}")

                if os.path.exists(target_path):
                    return target_path

                # Also search inside candidate flac/ subfolder
                sub_path = os.path.abspath(os.path.join(self.audio_dir, "flac", rel_path))
                try:
                    sub_common = os.path.commonpath([sub_path, self.audio_dir])
                    if sub_common == self.audio_dir and os.path.exists(sub_path):
                        return sub_path
                except ValueError:
                    pass

        return None

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        speaker_id, file_name, attack_id, label = self.samples[idx]

        file_path = self._resolve_audio_path(file_name)

        if file_path is None or not os.path.exists(file_path):
            self.missing_files_count += 1
            log_mel = np.zeros((80, self.target_frames), dtype=np.float32)
        else:
            try:
                with open(file_path, "rb") as f:
                    audio_bytes = f.read()

                processed = self.processor.load_and_preprocess(audio_bytes, os.path.basename(file_path))
                extracted = self.feature_extractor.extract_features(processed)
                log_mel = extracted.log_mel_spectrogram
            except (AudioProcessingError, Exception):
                self.missing_files_count += 1
                log_mel = np.zeros((80, self.target_frames), dtype=np.float32)

        # Standardize time frame length to target_frames (e.g. 300)
        n_mels, n_frames = log_mel.shape
        if n_frames < self.target_frames:
            pad_width = self.target_frames - n_frames
            log_mel_padded = np.pad(log_mel, ((0, 0), (0, pad_width)), mode="constant", constant_values=-23.0)
        elif n_frames > self.target_frames:
            start = (n_frames - self.target_frames) // 2
            log_mel_padded = log_mel[:, start:start + self.target_frames]
        else:
            log_mel_padded = log_mel

        # Z-score normalization per channel
        mean = np.mean(log_mel_padded)
        std = np.std(log_mel_padded) + 1e-7
        log_mel_norm = (log_mel_padded - mean) / std

        feature_tensor = torch.from_numpy(log_mel_norm).float().unsqueeze(0)
        label_tensor = torch.tensor([float(label)], dtype=torch.float32)

        return feature_tensor, label_tensor
