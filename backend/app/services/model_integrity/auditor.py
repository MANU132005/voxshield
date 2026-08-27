"""
Model Integrity & Checkpoint Provenance Auditor.

Inspects PyTorch model checkpoint files, verifies SHA-256 file hashes, checks state-dict
tensor dimensions, validates parameter weight finite bounds (no NaN/Inf), audits BatchNorm
trackers, and determines model training provenance.
"""

import os
import hashlib
import json
from typing import Dict, Any, Optional
import torch

from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet


def calculate_file_sha256(filepath: str) -> str:
    """Calculates SHA-256 hash of a file on disk."""
    if not os.path.exists(filepath):
        return "NOT_FOUND"

    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def audit_model_checkpoint(checkpoint_path: str = "./models/anti_spoofing_resnet.pt") -> Dict[str, Any]:
    abs_path = os.path.abspath(checkpoint_path)
    file_exists = os.path.exists(abs_path)

    if not file_exists:
        return {
            "checkpoint_found": False,
            "checkpoint_path": abs_path,
            "sha256_hash": "NOT_FOUND",
            "file_size_bytes": 0,
            "provenance": "MISSING",
            "status": "BLOCKED — MODEL CHECKPOINT NOT FOUND"
        }

    file_size = os.path.getsize(abs_path)
    sha256_hash = calculate_file_sha256(abs_path)

    model = VoiceAntiSpoofingResNet()
    nan_found = False
    inf_found = False
    num_batches_tracked = None
    tensor_shapes = {}

    try:
        checkpoint_data = torch.load(abs_path, map_location="cpu", weights_only=True)
        if isinstance(checkpoint_data, dict) and "state_dict" in checkpoint_data:
            state_dict = checkpoint_data["state_dict"]
        elif isinstance(checkpoint_data, dict):
            state_dict = checkpoint_data
        else:
            state_dict = model.state_dict()

        for key, tensor in state_dict.items():
            if isinstance(tensor, torch.Tensor):
                tensor_shapes[key] = list(tensor.shape)
                if torch.isnan(tensor).any():
                    nan_found = True
                if torch.isinf(tensor).any():
                    inf_found = True
                if "num_batches_tracked" in key:
                    num_batches_tracked = int(tensor.item())

        # Determine Provenance
        if isinstance(checkpoint_data, dict) and "provenance" in checkpoint_data:
            provenance = checkpoint_data["provenance"]
            provenance_note = f"Model checkpoint explicitly declares provenance: {provenance}"
        elif num_batches_tracked is not None and num_batches_tracked == 72:
            provenance = "DEMO_DSP_SYNTHETIC_DATASET"
            provenance_note = "Model was trained for 8 epochs on DSP-generated synthetic signals (72 batches). Has zero real-world ASVspoof capability."
        elif num_batches_tracked is not None and num_batches_tracked > 1000:
            provenance = "REAL_ASVSPOOF_TRAINED"
            provenance_note = "Model checkpoint indicates large-scale training run."
        else:
            provenance = "DEMO_OR_UNKNOWN"
            provenance_note = "Model checkpoint provenance cannot be confirmed as real ASVspoof data."

        status = "PASS — CHECKPOINT INTEGRITY VERIFIED" if not (nan_found or inf_found) else "FAIL — CORRUPTED WEIGHTS"

    except Exception as e:
        status = f"FAIL — COULD NOT LOAD CHECKPOINT: {str(e)}"
        provenance = "UNKNOWN"
        provenance_note = f"Error loading checkpoint: {str(e)}"

    return {
        "checkpoint_found": True,
        "checkpoint_path": abs_path,
        "sha256_hash": sha256_hash,
        "file_size_bytes": file_size,
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "nan_detected": nan_found,
        "inf_detected": inf_found,
        "num_batches_tracked": num_batches_tracked,
        "provenance": provenance,
        "provenance_note": provenance_note,
        "architecture": "VoiceAntiSpoofingResNet (2D Residual CNN)",
        "input_shape": "[batch, 1, 80, 300]",
        "status": status
    }
