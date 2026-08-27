"""
Dataset Gate Module.

Audits dataset root, protocol files, audio FLAC presence, readability, duration sanity,
and format validity.
"""

import os
from typing import Dict, Any, Tuple
from app.services.evaluation.types import DatasetGateStatus
from scripts.audit_asvspoof import audit_asvspoof_dataset


class DatasetGate:
    def verify_dataset(self, root_path: str = "./datasets/ASVspoof2019_LA/LA") -> Tuple[DatasetGateStatus, Dict[str, Any]]:
        abs_root = os.path.abspath(root_path)

        if not os.path.exists(abs_root):
            return DatasetGateStatus.DATASET_MISSING, {
                "dataset_found": False,
                "dataset_root": abs_root,
                "error": "Dataset root directory does not exist."
            }

        audit_res = audit_asvspoof_dataset(root_path=abs_root)
        if not audit_res["dataset_found"]:
            return DatasetGateStatus.DATASET_MISSING, audit_res

        protocols = audit_res.get("protocols_found", {})
        if not (protocols.get("train") and protocols.get("dev") and protocols.get("eval")):
            return DatasetGateStatus.DATASET_PARTIAL, audit_res

        return DatasetGateStatus.DATASET_READY, audit_res
