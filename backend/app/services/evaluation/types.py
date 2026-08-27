"""
VoxShield Real-World Evaluation Orchestrator & Benchmark Gate — Data Types.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class DatasetGateStatus(str, Enum):
    DATASET_READY = "DATASET_READY"
    DATASET_PARTIAL = "DATASET_PARTIAL"
    DATASET_INVALID = "DATASET_INVALID"
    DATASET_MISSING = "DATASET_MISSING"
    DATASET_CORRUPTED = "DATASET_CORRUPTED"


class CheckpointGateStatus(str, Enum):
    CHECKPOINT_VALID = "CHECKPOINT_VALID"
    CHECKPOINT_INVALID = "CHECKPOINT_INVALID"
    CHECKPOINT_MISSING = "CHECKPOINT_MISSING"
    PROVENANCE_BLOCKED = "PROVENANCE_BLOCKED"


class LeakageGateStatus(str, Enum):
    LEAKAGE_FREE = "LEAKAGE_FREE"
    LEAKAGE_DETECTED = "LEAKAGE_DETECTED"
    LEAKAGE_AUDIT_BLOCKED = "LEAKAGE_AUDIT_BLOCKED"


class CalibrationStatus(str, Enum):
    CALIBRATED = "CALIBRATED"
    UNCALIBRATED = "UNCALIBRATED"
    CALIBRATION_BLOCKED = "CALIBRATION_BLOCKED"


class BenchmarkGateStatus(str, Enum):
    BLOCKED = "BLOCKED"
    READY_FOR_EVALUATION = "READY_FOR_EVALUATION"
    EVALUATED = "EVALUATED"
    CERTIFIED = "CERTIFIED"


@dataclass
class MetricResult:
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    roc_auc: Optional[float]
    eer: Optional[float]
    eer_threshold: Optional[float]
    far: Optional[float]
    frr: Optional[float]
    confusion_matrix: Optional[Dict[str, int]]
    sample_count: int


@dataclass
class ConfidenceIntervalResult:
    metric_name: str
    point_estimate: float
    lower_bound: float
    upper_bound: float
    confidence_level: float
    bootstrap_count: int


@dataclass
class CalibrationMetadata:
    status: str                         # CalibrationStatus enum value
    method: str                         # e.g., Platt Scaling, Isotonic, Uncalibrated
    sample_count: int
    brier_score: Optional[float]
    expected_calibration_error: Optional[float]


@dataclass
class OrchestratorStage:
    stage_id: int
    stage_name: str
    status: str
    duration_ms: float
    errors: List[str]
    warnings: List[str]
    evidence: Dict[str, Any]


@dataclass
class OrchestratorResult:
    overall_status: str                 # BLOCKED, FAILED, COMPLETED
    benchmark_certification: str        # BenchmarkGateStatus enum value
    dataset_status: str                 # DatasetGateStatus enum value
    checkpoint_status: str              # CheckpointGateStatus enum value
    leakage_status: str                 # LeakageGateStatus enum value
    metrics: Optional[Dict[str, Any]]
    confidence_intervals: Optional[List[Dict[str, Any]]]
    calibration: Dict[str, Any]
    claim_matrix: Dict[str, str]
    stages: List[Dict[str, Any]]
