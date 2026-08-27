"""
Leakage Gate Module.

Audits cross-split utterance and speaker overlap across train, dev, and eval dataset splits.
"""

from typing import Dict, Any, Tuple
from app.services.evaluation.types import LeakageGateStatus


class LeakageGate:
    def audit_leakage(self, audit_res: Dict[str, Any]) -> Tuple[LeakageGateStatus, Dict[str, Any]]:
        if not audit_res.get("dataset_found"):
            return LeakageGateStatus.LEAKAGE_AUDIT_BLOCKED, {
                "leakage_free": False,
                "error": "Cannot audit leakage on missing dataset."
            }

        leakage_info = audit_res.get("cross_split_leakage", {})
        has_leakage = leakage_info.get("train_eval_utterance_overlap", 0) > 0 or leakage_info.get("train_dev_utterance_overlap", 0) > 0

        if has_leakage:
            return LeakageGateStatus.LEAKAGE_DETECTED, leakage_info

        return LeakageGateStatus.LEAKAGE_FREE, leakage_info
