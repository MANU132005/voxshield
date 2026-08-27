# Milestone 7: Official Dataset Specification & Research Report
## ASVspoof 2019 Logical Access (LA) Dataset

---

### 1. Official Dataset Overview
- **Official Title**: ASVspoof 2019: The 3rd Automatic Speaker Verification Spoofing and Countermeasures Challenge Database.
- **Primary Source**: ASVspoof Consortium / Edinburgh DataShare (`https://datashare.ed.ac.uk/handle/10283/3336`).
- **Domain**: Voice Anti-Spoofing, Text-to-Speech (TTS) Deepfake Detection, Voice Conversion (VC) Countermeasures.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0).

---

### 2. Dataset Partitions & Sample Counts

| Partition | Purpose | Bona-Fide (Genuine) Samples | Spoofed (Deepfake) Samples | Total Samples | Attack Algorithms |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`ASVspoof2019_LA_train`** | Training Set | 2,580 | 22,800 | 25,380 | A01 – A06 (Known) |
| **`ASVspoof2019_LA_dev`** | Validation / Dev Set | 2,548 | 22,296 | 24,844 | A01 – A06 (Known) |
| **`ASVspoof2019_LA_eval`** | Benchmark Evaluation | 7,355 | 63,882 | 71,237 | A07 – A19 (Unseen) |
| **Total** | Full Benchmark | **12,483** | **108,978** | **121,461** | **A01 – A19** |

---

### 3. Audio Specifications
- **Audio Format**: FLAC (Free Lossless Audio Codec), 16-bit PCM.
- **Sampling Rate**: 16,000 Hz (16 kHz).
- **Channels**: 1 (Mono).
- **Duration**: ~1.5s to ~5.0s per utterance (average ~2.8s).

---

### 4. Protocol File Format
The official protocol files (`ASVspoof2019.LA.cm.train.trn.txt`, `ASVspoof2019.LA.cm.dev.trl.txt`, `ASVspoof2019.LA.cm.eval.trl.txt`) follow a space-delimited structure:

```text
[SPEAKER_ID] [AUDIO_FILE_NAME] [ENV_ID] [ATTACK_ID] [KEY]
LA_0079      LA_E_2834728      -        -           bonafide
LA_0079      LA_E_9934811      -        A07         spoof
```

- **`KEY` Mapping**:
  - `bonafide` $\rightarrow$ Genuine speech (Label `0`)
  - `spoof` $\rightarrow$ AI-generated / converted speech (Label `1`)

---

### 5. Attack Algorithms Summary
- **Train/Dev Attacks (A01–A06)**: Neural Vocoders (WaveNet), Concatenative TTS, Spectral Voice Conversion.
- **Eval Attacks (A07–A19)**: 13 zero-day unseen attack algorithms including modern neural Vocoders (HiFi-GAN, WaveGlow), transfer-learning voice conversion, and waveform-filtering spoofing.

---

### 6. Storage & System Footprint
- **Compressed Archive Footprint**: ~6.5 GB
- **Uncompressed FLAC Footprint**: ~15.2 GB
- **Cached Log-Mel Feature Footprint**: ~3.4 GB
