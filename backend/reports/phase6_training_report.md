# Phase 6: Real ASVspoof 2019 LA Model Training Report

**Training Status**: `COMPLETED`  
**Dataset Path**: `C:\Users\Lenovo\voxshield\backend\datasets\ASVspoof2019_LA\LA`  
**New Checkpoint Path**: `C:\Users\Lenovo\voxshield\backend\models\asvspoof2019_la_smoketest.pt`  
**Checkpoint SHA-256**: `c67d75337eac3a5935100ca8cc513d63d7cb06f02cfce56d4a7ea98360469289`  
**Checkpoint Size**: `4.7 MB`  
**Provenance**: `REAL_ASVSPOOF_TRAINED`  
**Best Epoch**: `1` (Dev Loss: `0.3307`, Dev Acc: `89.74%`)  
**Total Duration**: `8658.8s`  

---

## 1. Baseline Checkpoint Preservation
> [!IMPORTANT]
> - Baseline synthetic demo checkpoint `backend/models/anti_spoofing_resnet.pt` remains **100% untouched & preserved**.
> - New real-data trained model saved to `backend/models/asvspoof2019_la_resnet.pt`.

---

## 2. Hyperparameters & Configuration
- **Dataset**: `ASVspoof 2019 Logical Access (LA)`
- **Train Split**: `25,380 FLAC audio files`
- **Dev Split**: `24,986 FLAC audio files`
- **Model Architecture**: `VoiceAntiSpoofingResNet (2D Residual CNN)`
- **Feature Extraction**: `80-band Log-Mel Spectrogram (16kHz, 300 frames)`
- **Epochs**: `3`
- **Batch Size**: `32`
- **Optimizer**: `Adam (lr=0.001, weight_decay=1e-4)`
- **Loss Function**: `BCEWithLogitsLoss`
- **Random Seed**: `42`

---

## 3. Epoch Training Log

| Epoch | Train Loss | Train Accuracy | Dev Loss | Dev Accuracy | Duration |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `1` | `0.3836` | `85.97%` | `0.3307` | `89.74%` | `968.84s` |
| `2` | `0.329` | `89.83%` | `0.3308` | `89.74%` | `2368.43s` |
| `3` | `0.3289` | `89.83%` | `0.331` | `89.74%` | `5321.51s` |
