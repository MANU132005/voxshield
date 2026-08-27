"""
Checkpoint Gate Module.

Audits PyTorch checkpoint file existence, SHA-256 hash, file size, state-dict tensor shapes,
NaN/Inf weight checks, BatchNorm tracker state, and provenance.
"""

import os
from typing import Dict, Any, Tuple
from app.services.evaluation.types import CheckpointGateStatus
from app.services.model_integrity.auditor import audit_model_checkpoint


class CheckpointGate:
    def verify_checkpoint(self, checkpoint_path: str = "./models/anti_spoofing_resnet.pt") -> Tuple[CheckpointGateStatus, Dict[str, Any]]:
        abs_path = os.path.abspath(checkpoint_path)

        if not os.path.exists(abs_path):
            return CheckpointGateStatus.CHECKPOINT_MISSING, {
                "checkpoint_found": False,
                "checkpoint_path": abs_path,
                "error": "Checkpoint file not found on disk."
            }

        audit_res = audit_model_checkpoint(checkpoint_path=abs_path)

        if audit_res.get("nan_detected") or audit_res.get("inf_detected"):
            return CheckpointGateStatus.CHECKPOINT_INVALID, audit_res

        if audit_res.get("provenance") == "DEMO_DSP_SYNTHETIC_DATASET":
            return CheckpointGateStatus.PROVENANCE_BLOCKED, audit_res

        return CheckpointGateStatus.CHECKPOINT_VALID, audit_res
