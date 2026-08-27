"""
Phase 6 Dataset Discovery & Audit Engine — Data Types & Models.
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class DatasetStatus(str, Enum):
    BLOCKED_DATASET = "BLOCKED_DATASET"
    DATASET_MISSING = "DATASET_MISSING"
    DATASET_DISCOVERED = "DATASET_DISCOVERED"
    INTEGRITY_VERIFIED = "INTEGRITY_VERIFIED"
    CORRUPT_FILES_DETECTED = "CORRUPT_FILES_DETECTED"
    PROTOCOL_MISMATCH = "PROTOCOL_MISMATCH"
    LEAKAGE_DETECTED = "LEAKAGE_DETECTED"


@dataclass
class SplitAudit:
    split_name: str                  # train, dev, eval
    audio_file_count: int
    protocol_line_count: int
    speakers_count: int
    bonafide_count: int
    spoof_count: int
    missing_audio_files: List[str]
    corrupt_audio_files: List[str]


@dataclass
class DatasetAuditResult:
    dataset_name: str                # ASVspoof 2019 Logical Access
    dataset_root: str
    status: str                      # DatasetStatus enum value
    is_valid: bool
    train_split: Optional[SplitAudit]
    dev_split: Optional[SplitAudit]
    eval_split: Optional[SplitAudit]
    total_audio_files: int
    total_protocol_entries: int
    sample_rate_hz: int
    duration_stats_seconds: Dict[str, float]
    leakage_detected: bool
    leakage_details: List[str]
    disclosures: List[str]
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
