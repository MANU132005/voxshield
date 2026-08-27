# VoxShield M14 — Demo Model vs. Real-Data Model Comparison

| Dimension | Demo Checkpoint (`anti_spoofing_resnet.pt`) | Real-Data Checkpoint (`anti_spoofing_asvspoof2019_la.pt`) |
| :--- | :--- | :--- |
| **Provenance** | `DEMO_DSP_SYNTHETIC_DATASET` | `ASVSPOOF2019_LA_TRAINED` |
| **Training Data** | 800 synthetic DSP-generated audio signals | 25,380 official ASVspoof 2019 LA FLAC samples |
| **BatchNorm Batches**| 72 batches | > 1,000 batches |
| **Real-World Capability**| **ZERO** (Demo/Engineering pipeline check only) | **HIGH** (Trained on real vocoders & TTS attacks) |
| **Current Status** | **ACTIVE & PRESERVED** | **NOT CREATED (DATASET MISSING)** |
