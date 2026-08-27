"""
Phase 5 Live Detection Latency Benchmark & Report Generator.

Measures cold-start, warm, per-window, and total live analysis processing overhead.
Generates phase5_live_detection_report.md and phase5_live_detection_status.json.
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.audio.processor import AudioProcessor
from app.services.live_detection.live_engine import LiveDetectionEngine
from app.services.live_detection.reports import generate_phase5_reports
from tests.test_processor import create_synthetic_wav_bytes


def main():
    print("========================================================")
    print("VOXSHIELD PHASE 5 — LIVE DETECTION ENGINE BENCHMARK")
    print("========================================================")

    processor = AudioProcessor()
    live_engine = LiveDetectionEngine(audio_processor=processor)

    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=3.0, channels=1)
    processed_audio = processor.load_and_preprocess(wav_bytes, "phase5_test.wav")

    # Warm-up run
    res_warm = live_engine.analyze_live_audio(processed_audio)

    # 20 Benchmark runs
    total_latencies = []
    win_latencies = []

    for _ in range(20):
        t0 = time.perf_counter()
        res = live_engine.analyze_live_audio(processed_audio)
        total_latencies.append((time.perf_counter() - t0) * 1000.0)
        win_latencies.append(res.processing_metadata["mean_window_latency_ms"])

    mean_total = round(float(np.mean(total_latencies)), 2)
    mean_win = round(float(np.mean(win_latencies)), 2)

    res_warm.processing_metadata["total_duration_ms"] = mean_total
    res_warm.processing_metadata["mean_window_latency_ms"] = mean_win

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    report_paths = generate_phase5_reports(res_warm, output_dir=reports_dir)

    print(f"Live Analysis Status:     {res_warm.status}")
    print(f"Live Decision:            {res_warm.decision}")
    print(f"Confidence State:         {res_warm.confidence_state}")
    print(f"Detector Agreement:       {res_warm.agreement['agreement_state']}")
    print(f"Temporal Stability:       {res_warm.temporal_stability['stability_state']}")
    print(f"Mean Total Pipeline Latency (3.0s Audio): {mean_total} ms")
    print(f"Mean Per-Window Latency (1.0s Window):    {mean_win} ms")
    print(f"Saved reports to: {report_paths['md_report']} and {report_paths['json_report']}")


if __name__ == "__main__":
    import numpy as np
    main()
