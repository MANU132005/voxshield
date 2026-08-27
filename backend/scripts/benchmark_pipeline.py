"""
VoxShield Backend & Forensic Engine Performance Benchmark Script.

Executes component-level and end-to-end latency measurement across N iterations,
computing min, max, mean, median, p95, and p99 execution latencies in milliseconds.
Generates machine-readable JSON and human-readable Markdown reports.
"""

import os
import sys
import time
import json
import platform
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.audio.processor import AudioProcessor
from app.services.anti_spoofing.detector import AntiSpoofingDetector
from app.services.replay_detection.dsp import ReplayDetector
from app.services.risk_engine.evaluator import RiskEvaluator
from app.services.forensics.forensic_engine import ForensicEngine
from tests.test_processor import create_synthetic_wav_bytes


def compute_stats(latencies_ms: list) -> dict:
    arr = np.array(latencies_ms)
    return {
        "min_ms": round(float(np.min(arr)), 2),
        "max_ms": round(float(np.max(arr)), 2),
        "mean_ms": round(float(np.mean(arr)), 2),
        "median_ms": round(float(np.median(arr)), 2),
        "p95_ms": round(float(np.percentile(arr, 95)), 2),
        "p99_ms": round(float(np.percentile(arr, 99)), 2)
    }


def run_benchmark(iterations: int = 50) -> dict:
    print(f"--- Running VoxShield Backend & Forensic Engine Benchmark ({iterations} iterations) ---")

    processor = AudioProcessor()
    detector = AntiSpoofingDetector()
    replay_dsp = ReplayDetector()
    risk_evaluator = RiskEvaluator()
    forensic_engine = ForensicEngine()

    # Generate 1.0-second synthetic audio wave
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)

    latencies_prep = []
    latencies_feats = []
    latencies_nn = []
    latencies_dsp = []
    latencies_risk = []
    latencies_forensics = []
    latencies_e2e = []

    # Warmup iteration
    p_audio = processor.load_and_preprocess(wav_bytes, "warmup.wav")
    feats = processor.extract_features(p_audio)
    synth_res = detector.predict(feats)
    replay_res = replay_dsp.analyze_replay_detailed(p_audio)
    risk_evaluator.evaluate_risk(synth_res, replay_res, p_audio)
    forensic_engine.evaluate_forensics(synth_res.synthetic_score, replay_res.replay_score, p_audio.audio_signal, p_audio.sample_rate)

    for i in range(iterations):
        t_start = time.perf_counter()

        # 1. Preprocessing
        t0 = time.perf_counter()
        processed_audio = processor.load_and_preprocess(wav_bytes, f"bench_{i}.wav")
        t1 = time.perf_counter()
        latencies_prep.append((t1 - t0) * 1000.0)

        # 2. Feature Extraction
        t0 = time.perf_counter()
        extracted_features = processor.extract_features(processed_audio)
        t1 = time.perf_counter()
        latencies_feats.append((t1 - t0) * 1000.0)

        # 3. Neural Anti-Spoofing Inference
        t0 = time.perf_counter()
        synth_result = detector.predict(extracted_features)
        t1 = time.perf_counter()
        latencies_nn.append((t1 - t0) * 1000.0)

        # 4. Replay DSP Analysis
        t0 = time.perf_counter()
        replay_result = replay_dsp.analyze_replay_detailed(processed_audio)
        t1 = time.perf_counter()
        latencies_dsp.append((t1 - t0) * 1000.0)

        # 5. Risk Evaluation
        t0 = time.perf_counter()
        assessment = risk_evaluator.evaluate_risk(synth_result, replay_result, processed_audio)
        t1 = time.perf_counter()
        latencies_risk.append((t1 - t0) * 1000.0)

        # 6. Forensic Intelligence Analysis
        t0 = time.perf_counter()
        forensic_assessment = forensic_engine.evaluate_forensics(
            synth_result.synthetic_score, replay_result.replay_score, processed_audio.audio_signal, processed_audio.sample_rate
        )
        t1 = time.perf_counter()
        latencies_forensics.append((t1 - t0) * 1000.0)

        t_end = time.perf_counter()
        latencies_e2e.append((t_end - t_start) * 1000.0)

    stats = {
        "environment": {
            "python_version": sys.version.split()[0],
            "os": platform.platform(),
            "cpu_cores": os.cpu_count() or 1,
            "torch_version": "2.13.0+cpu"
        },
        "benchmark_config": {
            "iterations": iterations,
            "sample_duration_seconds": 1.0,
            "sample_rate": 16000
        },
        "latency_statistics": {
            "audio_preprocessing": compute_stats(latencies_prep),
            "feature_extraction": compute_stats(latencies_feats),
            "neural_anti_spoofing_inference": compute_stats(latencies_nn),
            "acoustic_replay_dsp": compute_stats(latencies_dsp),
            "risk_evaluation": compute_stats(latencies_risk),
            "forensic_intelligence_engine": compute_stats(latencies_forensics),
            "end_to_end_pipeline": compute_stats(latencies_e2e)
        }
    }

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)

    json_path = os.path.join(reports_dir, "m15_forensic_benchmark.json")
    md_path = os.path.join(reports_dir, "m15_forensic_benchmark.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    e2e = stats["latency_statistics"]["end_to_end_pipeline"]
    prep = stats["latency_statistics"]["audio_preprocessing"]
    feat = stats["latency_statistics"]["feature_extraction"]
    nn = stats["latency_statistics"]["neural_anti_spoofing_inference"]
    dsp = stats["latency_statistics"]["acoustic_replay_dsp"]
    risk = stats["latency_statistics"]["risk_evaluation"]
    forensic = stats["latency_statistics"]["forensic_intelligence_engine"]

    md_content = f"""# VoxShield M15 — Forensic Engine Benchmark Report

**Benchmark Date**: {time.strftime("%Y-%m-%d %H:%M:%S")}  
**Iterations**: `{iterations}`  
**Audio Signal Duration**: `1.0 sec (16,000 Hz Mono)`  
**Environment**: `Python {stats['environment']['python_version']} on {stats['environment']['os']}`  

---

## 1. End-to-End & Component Latency Summary

| Pipeline Component | Min (ms) | Mean (ms) | Median (ms) | P95 (ms) | P99 (ms) | Max (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Audio Preprocessing** | {prep['min_ms']} | {prep['mean_ms']} | {prep['median_ms']} | {prep['p95_ms']} | {prep['p99_ms']} | {prep['max_ms']} |
| **2. Feature Extraction** | {feat['min_ms']} | {feat['mean_ms']} | {feat['median_ms']} | {feat['p95_ms']} | {feat['p99_ms']} | {feat['max_ms']} |
| **3. Neural AI Inference** | {nn['min_ms']} | {nn['mean_ms']} | {nn['median_ms']} | {nn['p95_ms']} | {nn['p99_ms']} | {nn['max_ms']} |
| **4. Acoustic Replay DSP** | {dsp['min_ms']} | {dsp['mean_ms']} | {dsp['median_ms']} | {dsp['p95_ms']} | {dsp['p99_ms']} | {dsp['max_ms']} |
| **5. Risk Evaluation** | {risk['min_ms']} | {risk['mean_ms']} | {risk['median_ms']} | {risk['p95_ms']} | {risk['p99_ms']} | {risk['max_ms']} |
| **6. Forensic Engine Analysis** | {forensic['min_ms']} | {forensic['mean_ms']} | {forensic['median_ms']} | {forensic['p95_ms']} | {forensic['p99_ms']} | {forensic['max_ms']} |
| **TOTAL END-TO-END PIPELINE** | **{e2e['min_ms']}** | **{e2e['mean_ms']}** | **{e2e['median_ms']}** | **{e2e['p95_ms']}** | **{e2e['p99_ms']}** | **{e2e['max_ms']}** |

---

## 2. Performance & Throughput Findings
- **Mean Forensic Engine Analysis Latency**: `{forensic['mean_ms']} ms`
- **Mean Total End-to-End Pipeline Latency**: `{e2e['mean_ms']} ms`
- **P95 Latency**: `{e2e['p95_ms']} ms`
- **Throughput**: ~`{round(1000.0 / e2e['mean_ms'], 1)} requests/sec` per CPU core.
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Forensic Benchmark completed successfully! Reports saved to {json_path} and {md_path}")
    return stats


if __name__ == "__main__":
    run_benchmark(iterations=50)
