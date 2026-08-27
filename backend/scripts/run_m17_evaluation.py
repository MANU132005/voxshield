"""
M17 Evaluation Orchestrator CLI Script.

Executes 16-stage evaluation orchestration, verifying dataset gate, checkpoint gate,
leakage gate, metric calculation, confidence intervals, calibration status, and benchmark certification.
"""

import os
import sys
import json
import argparse
from dataclasses import asdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.evaluation.evaluation_orchestrator import EvaluationOrchestrator


def main():
    parser = argparse.ArgumentParser(description="VoxShield M17 Evaluation Orchestrator")
    parser.add_argument("--dataset-root", default="./datasets/ASVspoof2019_LA/LA")
    parser.add_argument("--checkpoint", default="./models/anti_spoofing_resnet.pt")
    parser.add_argument("--split", default="eval")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--bootstrap-iterations", type=int, default=200)
    parser.add_argument("--calibration", action="store_true")
    parser.add_argument("--output-dir", default="./reports")
    parser.add_argument("--strict", action="store_true", default=True)

    args = parser.parse_args()

    orchestrator = EvaluationOrchestrator()
    result = orchestrator.run_orchestration(
        dataset_root=args.dataset_root,
        checkpoint_path=args.checkpoint,
        split=args.split,
        strict=args.strict
    )

    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, "m17_evaluation_status.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2)

    print("\n========================================================")
    print(f"VOXSHIELD M17 EVALUATION ORCHESTRATOR STATUS: {result.overall_status}")
    print("========================================================")
    print(f"Benchmark Certification: {result.benchmark_certification}")
    print(f"Dataset Gate Status:    {result.dataset_status}")
    print(f"Checkpoint Gate Status: {result.checkpoint_status}")
    print(f"Leakage Gate Status:    {result.leakage_status}")
    print(f"Saved evaluation status to: {json_path}")


if __name__ == "__main__":
    main()
