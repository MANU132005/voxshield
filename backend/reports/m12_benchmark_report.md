# VoxShield M12 — Performance Benchmark Report

**Benchmark Date**: 2026-08-24 23:55:57  
**Iterations**: `50`  
**Audio Signal Duration**: `1.0 sec (16,000 Hz Mono)`  
**Environment**: `Python 3.11.9 on Windows-10-10.0.26200-SP0`  

---

## 1. End-to-End & Component Latency Summary

| Pipeline Component | Min (ms) | Mean (ms) | Median (ms) | P95 (ms) | P99 (ms) | Max (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Audio Preprocessing** | 0.07 | 0.13 | 0.14 | 0.17 | 0.19 | 0.19 |
| **2. Feature Extraction** | 1.81 | 2.67 | 2.68 | 3.16 | 3.83 | 3.99 |
| **3. Neural AI Inference** | 4.95 | 6.48 | 6.36 | 7.69 | 8.86 | 9.0 |
| **4. Acoustic Replay DSP** | 1.42 | 2.27 | 2.42 | 2.57 | 2.7 | 2.76 |
| **5. Threat Risk Assessment** | 0.08 | 0.14 | 0.15 | 0.18 | 0.21 | 0.22 |
| **TOTAL END-TO-END PIPELINE** | **9.1** | **11.71** | **11.79** | **13.18** | **14.25** | **14.33** |

---

## 2. Performance & Throughput Findings
- **Mean End-to-End Pipeline Latency**: `11.71 ms`
- **P95 Latency**: `13.18 ms`
- **Throughput**: ~`85.4 requests/sec` per CPU core.
