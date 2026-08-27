# VoxShield M15 — Forensic Engine Benchmark Report

**Benchmark Date**: 2026-08-25 00:15:08  
**Iterations**: `50`  
**Audio Signal Duration**: `1.0 sec (16,000 Hz Mono)`  
**Environment**: `Python 3.11.9 on Windows-10-10.0.26200-SP0`  

---

## 1. End-to-End & Component Latency Summary

| Pipeline Component | Min (ms) | Mean (ms) | Median (ms) | P95 (ms) | P99 (ms) | Max (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Audio Preprocessing** | 0.17 | 0.29 | 0.29 | 0.35 | 0.39 | 0.42 |
| **2. Feature Extraction** | 3.42 | 5.42 | 5.57 | 5.91 | 6.03 | 6.06 |
| **3. Neural AI Inference** | 7.74 | 16.93 | 17.66 | 18.33 | 19.74 | 20.98 |
| **4. Acoustic Replay DSP** | 2.31 | 4.6 | 4.76 | 5.02 | 5.2 | 5.29 |
| **5. Risk Evaluation** | 0.17 | 0.3 | 0.31 | 0.35 | 0.39 | 0.41 |
| **6. Forensic Engine Analysis** | 3.97 | 8.89 | 9.28 | 9.68 | 9.89 | 9.89 |
| **TOTAL END-TO-END PIPELINE** | **18.28** | **36.44** | **37.84** | **38.85** | **40.9** | **42.2** |

---

## 2. Performance & Throughput Findings
- **Mean Forensic Engine Analysis Latency**: `8.89 ms`
- **Mean Total End-to-End Pipeline Latency**: `36.44 ms`
- **P95 Latency**: `38.85 ms`
- **Throughput**: ~`27.4 requests/sec` per CPU core.
