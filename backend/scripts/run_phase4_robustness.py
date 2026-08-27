"""
Phase 4 Real-World Security & Robustness Evaluation CLI Script.

Executes baseline vs transformed audio evaluations across all 7 robustness conditions and generates reports.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.audio.processor import AudioProcessor
from app.services.robustness.runner import RobustnessRunner
from app.services.robustness.reports import generate_phase4_reports
from tests.test_processor import create_synthetic_wav_bytes


def main():
    print("========================================================")
    print("VOXSHIELD PHASE 4 — REAL-WORLD SECURITY & ROBUSTNESS AUDIT")
    print("========================================================")

    processor = AudioProcessor()
    runner = RobustnessRunner()

    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    processed_audio = processor.load_and_preprocess(wav_bytes, "phase4_test.wav")

    assessment = runner.run_standard_suite(processed_audio)

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    report_paths = generate_phase4_reports(assessment, output_dir=reports_dir)

    print(f"Phase 4 Robustness Evaluation Status: {assessment.overall_status}")
    print(f"Conditions Evaluated: {assessment.conditions_evaluated}")
    print(f"Stable Conditions:    {assessment.conditions_stable_count} / {assessment.conditions_evaluated}")
    print(f"Stability Ratio:      {assessment.stability_ratio}")
    print(f"Mean Trans Latency:   {assessment.mean_transformation_latency_ms} ms")
    print(f"Saved reports to: {report_paths['md_report']} and {report_paths['json_report']}")


if __name__ == "__main__":
    main()
