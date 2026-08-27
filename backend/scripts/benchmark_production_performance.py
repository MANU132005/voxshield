"""
VoxShield Production Performance & Latency Benchmarking Script.

Measures precise millisecond breakdowns for:
1. File read
2. Audio decoding (soundfile)
3. Audio preprocessing & resampling
4. Feature extraction (Log-Mel 80x300)
5. Tensor preparation
6. Neural Network Inference (VoiceAntiSpoofingResNet)
7. Total End-to-End Latency
"""

import os
import sys
import time
import numpy as np
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.audio.processor import AudioProcessor
from app.services.audio.features import FeatureExtractor
from app.services.anti_spoofing.detector import AntiSpoofingDetector


def run_latency_benchmark(num_trials: int = 50):
    print("========================================================")
    print("VOXSHIELD PRODUCTION PERFORMANCE & LATENCY BENCHMARK")
    print("========================================================")

    test_flac = os.path.abspath("datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_train/flac/LA_T_1138215.flac")
    if not os.path.exists(test_flac):
        print(f"Error: Benchmark file {test_flac} not found.")
        sys.exit(1)

    print(f"Benchmark File: {os.path.basename(test_flac)}")
    print(f"Number of Trials: {num_trials}")

    processor = AudioProcessor(target_sample_rate=16000, min_duration_seconds=0.5)
    extractor = FeatureExtractor(sample_rate=16000)
    detector = AntiSpoofingDetector()

    print(f"Loaded Model Checkpoint: {detector.model_path}")

    # Warmup pass
    with open(test_flac, "rb") as f:
        raw_bytes = f.read()
    proc = processor.load_and_preprocess(raw_bytes, os.path.basename(test_flac))
    feats = extractor.extract_features(proc)
    res = detector.predict(feats)

    # Benchmark loop
    read_times = []
    decode_preprocess_times = []
    feat_extract_times = []
    inference_times = []
    total_times = []

    for i in range(num_trials):
        t0 = time.perf_counter()

        with open(test_flac, "rb") as f:
            raw_b = f.read()
        t1 = time.perf_counter()

        proc_audio = processor.load_and_preprocess(raw_b, os.path.basename(test_flac))
        t2 = time.perf_counter()

        extracted = extractor.extract_features(proc_audio)
        t3 = time.perf_counter()

        result = detector.predict(extracted)
        t4 = time.perf_counter()

        read_times.append((t1 - t0) * 1000.0)
        decode_preprocess_times.append((t2 - t1) * 1000.0)
        feat_extract_times.append((t3 - t2) * 1000.0)
        inference_times.append((t4 - t3) * 1000.0)
        total_times.append((t4 - t0) * 1000.0)

    print("\n--- MEASURED LATENCY BREAKDOWN (MEAN ± STD) ---")
    print(f"1. Disk Read Latency             : {np.mean(read_times):.2f} ± {np.std(read_times):.2f} ms")
    print(f"2. Audio Decoding & Preprocessing : {np.mean(decode_preprocess_times):.2f} ± {np.std(decode_preprocess_times):.2f} ms")
    print(f"3. Feature Extraction (Log-Mel)  : {np.mean(feat_extract_times):.2f} ± {np.std(feat_extract_times):.2f} ms")
    print(f"4. PyTorch Model Inference       : {np.mean(inference_times):.2f} ± {np.std(inference_times):.2f} ms")
    print(f"--------------------------------------------------------")
    print(f"TOTAL END-TO-END LATENCY         : {np.mean(total_times):.2f} ± {np.std(total_times):.2f} ms")
    print(f"PERFORMANCE THROUGHPUT           : {1000.0 / np.mean(total_times):.1f} single-file inferences/sec")
    print("========================================================")

    return {
        "mean_read_ms": round(float(np.mean(read_times)), 2),
        "mean_decode_preprocess_ms": round(float(np.mean(decode_preprocess_times)), 2),
        "mean_feature_extract_ms": round(float(np.mean(feat_extract_times)), 2),
        "mean_inference_ms": round(float(np.mean(inference_times)), 2),
        "mean_total_ms": round(float(np.mean(total_times)), 2),
        "throughput_fps": round(float(1000.0 / np.mean(total_times)), 1)
    }


if __name__ == "__main__":
    run_latency_benchmark()
