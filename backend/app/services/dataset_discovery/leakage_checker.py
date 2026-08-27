"""
Phase 6 Data Leakage Prevention Engine Module.

Audits train/dev/eval splits for speaker overlap, duplicate audio hashes,
protocol contamination, and model provenance leakage.
"""

from typing import List, Set, Dict, Any, Tuple


class DataLeakageChecker:
    def check_speaker_leakage(
        self,
        train_speakers: Set[str],
        dev_speakers: Set[str],
        eval_speakers: Set[str]
    ) -> Tuple[bool, List[str]]:
        issues = []
        train_dev = train_speakers.intersection(dev_speakers)
        train_eval = train_speakers.intersection(eval_speakers)
        dev_eval = dev_speakers.intersection(eval_speakers)

        if train_dev:
            issues.append(f"Speaker leakage between Train and Dev splits: {len(train_dev)} overlapping speakers ({list(train_dev)[:3]}).")
        if train_eval:
            issues.append(f"Speaker leakage between Train and Eval splits: {len(train_eval)} overlapping speakers ({list(train_eval)[:3]}).")
        if dev_eval:
            issues.append(f"Speaker leakage between Dev and Eval splits: {len(dev_eval)} overlapping speakers ({list(dev_eval)[:3]}).")

        has_leakage = len(issues) > 0
        return has_leakage, issues

    def check_audio_hash_leakage(
        self,
        train_hashes: Set[str],
        dev_hashes: Set[str],
        eval_hashes: Set[str]
    ) -> Tuple[bool, List[str]]:
        issues = []
        train_dev = train_hashes.intersection(dev_hashes)
        train_eval = train_hashes.intersection(eval_hashes)
        dev_eval = dev_hashes.intersection(eval_hashes)

        if train_dev:
            issues.append(f"Audio payload leakage between Train and Dev splits: {len(train_dev)} duplicate files.")
        if train_eval:
            issues.append(f"Audio payload leakage between Train and Eval splits: {len(train_eval)} duplicate files.")
        if dev_eval:
            issues.append(f"Audio payload leakage between Dev and Eval splits: {len(dev_eval)} duplicate files.")

        has_leakage = len(issues) > 0
        return has_leakage, issues

    def check_model_checkpoint_leakage(self, provenance_info: Dict[str, Any]) -> Tuple[bool, List[str]]:
        issues = []
        provenance = provenance_info.get("provenance", provenance_info.get("model_provenance", ""))
        if "DEMO" in provenance.upper() or "SYNTHETIC" in provenance.upper():
            issues.append(
                f"Model provenance leakage detected: Checkpoint provenance '{provenance}' indicates synthetic demo data; "
                "cannot be submitted for real ASVspoof benchmark certification."
            )

        has_leakage = len(issues) > 0
        return has_leakage, issues
