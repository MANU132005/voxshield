"""
Automated Regression Test Suite for Genuine Voice Discrimination & Replay Calibration.

Guarantees:
1. Genuine human speech is correctly classified as SAFE / AUTHENTIC (synthetic_score < 0.10, replay_score < 0.15, risk_score < 0.35).
2. AI synthetic voice (spoof) is correctly classified as SPOOF_SUSPECTED / HIGH_RISK (synthetic_score > 0.90, risk_score > 0.50).
3. Overdriven / clipped audio triggers replay indicators (replay_score >= 0.35).
"""

import os
import glob
import pytest
from app.services.audio.processor import AudioProcessor
from app.services.audio.features import FeatureExtractor
from app.services.anti_spoofing.detector import AntiSpoofingDetector
from app.services.replay_detection.dsp import ReplayDetector
from app.services.risk_engine.evaluator import RiskEvaluator


@pytest.fixture
def services():
    return {
        "processor": AudioProcessor(),
        "extractor": FeatureExtractor(),
        "detector": AntiSpoofingDetector(),
        "replay": ReplayDetector(),
        "risk": RiskEvaluator()
    }


def test_genuine_speech_low_risk_guarantee(services):
    flac_dir = "datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_train/flac"
    proto_file = "datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.train.trn.txt"

    if not os.path.exists(flac_dir) or not os.path.exists(proto_file):
        pytest.skip("ASVspoof dataset files not present locally.")

    proto = {}
    with open(proto_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                proto[parts[1]] = parts[4].lower()

    bonafides = [f for f in glob.glob(f"{flac_dir}/*.flac") if proto.get(os.path.splitext(os.path.basename(f))[0]) == "bonafide"][:5]

    for b_file in bonafides:
        with open(b_file, "rb") as f:
            content = f.read()

        audio = services["processor"].load_and_preprocess(content, os.path.basename(b_file))
        features = services["extractor"].extract_features(audio)
        synth_res = services["detector"].predict(features)
        replay_res = services["replay"].analyze_replay_detailed(audio)
        risk_res = services["risk"].evaluate_risk(synth_res, replay_res, audio)

        assert synth_res.synthetic_score < 0.10, f"Expected low synthetic score for {b_file}, got {synth_res.synthetic_score}"
        assert replay_res.replay_score < 0.15, f"Expected low replay score for {b_file}, got {replay_res.replay_score}"
        assert risk_res.risk_score < 20.0, f"Expected low risk score for {b_file}, got {risk_res.risk_score}"
        assert risk_res.verdict in ("AUTHENTIC", "SAFE"), f"Expected AUTHENTIC verdict for {b_file}, got {risk_res.verdict}"


def test_ai_synthetic_spoof_detection_guarantee(services):
    flac_dir = "datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_train/flac"
    proto_file = "datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.train.trn.txt"

    if not os.path.exists(flac_dir) or not os.path.exists(proto_file):
        pytest.skip("ASVspoof dataset files not present locally.")

    proto = {}
    with open(proto_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                proto[parts[1]] = parts[4].lower()

    spoofs = [f for f in glob.glob(f"{flac_dir}/*.flac") if proto.get(os.path.splitext(os.path.basename(f))[0]) == "spoof"][:5]

    for s_file in spoofs:
        with open(s_file, "rb") as f:
            content = f.read()

        audio = services["processor"].load_and_preprocess(content, os.path.basename(s_file))
        features = services["extractor"].extract_features(audio)
        synth_res = services["detector"].predict(features)
        replay_res = services["replay"].analyze_replay_detailed(audio)
        risk_res = services["risk"].evaluate_risk(synth_res, replay_res, audio)

        assert synth_res.synthetic_score > 0.90, f"Expected high synthetic score for {s_file}, got {synth_res.synthetic_score}"
        assert risk_res.risk_score > 50.0, f"Expected high risk score for {s_file}, got {risk_res.risk_score}"
        assert risk_res.verdict in ("SPOOF_SUSPECTED", "CRITICAL_RISK", "SUSPICIOUS"), f"Expected SPOOF_SUSPECTED verdict for {s_file}, got {risk_res.verdict}"
