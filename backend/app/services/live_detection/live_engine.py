"""
Phase 5 Live Detection Orchestrator Module.

Coordinates live windowing, multi-window evidence fusion, detector agreement analysis,
temporal stability evaluation, ClaimGuard enforcement, and response assembly.
"""

import time
from dataclasses import asdict
from typing import Dict, Any, List, Optional
import numpy as np

from app.services.audio.processor import AudioProcessor, ProcessedAudio
from app.services.anti_spoofing.detector import AntiSpoofingDetector
from app.services.anti_spoofing.generalization import GeneralizationExtractor
from app.services.replay_detection.dsp import ReplayDetector
from app.services.risk_engine.evaluator import RiskEvaluator
from app.services.forensics.forensic_engine import ForensicEngine
from app.services.model_integrity.claim_guard import ClaimGuard

from app.services.live_detection.types import (
    LiveWindow,
    DetectorContributions,
    TemporalStabilityResult,
    DetectorAgreementResult,
    LiveAnalysisResult,
    LiveConfidenceState
)
from app.services.live_detection.windowing import LiveWindowingSystem, WindowConfig
from app.services.live_detection.agreement_engine import DetectorAgreementEngine
from app.services.live_detection.temporal_fusion import TemporalFusionEngine


class LiveDetectionEngine:
    def __init__(
        self,
        audio_processor: AudioProcessor = None,
        detector: AntiSpoofingDetector = None,
        replay_dsp: ReplayDetector = None,
        risk_evaluator: RiskEvaluator = None,
        forensic_engine: ForensicEngine = None,
        generalization_extractor: GeneralizationExtractor = None
    ):
        self.audio_processor = audio_processor or AudioProcessor()
        self.detector = detector or AntiSpoofingDetector()
        self.replay_dsp = replay_dsp or ReplayDetector()
        self.risk_evaluator = risk_evaluator or RiskEvaluator()
        self.forensic_engine = forensic_engine or ForensicEngine()
        self.generalization_extractor = generalization_extractor or GeneralizationExtractor()

        self.windowing_system = LiveWindowingSystem()
        self.agreement_engine = DetectorAgreementEngine()
        self.fusion_engine = TemporalFusionEngine()
        self.claim_guard = ClaimGuard(dataset_available=False, real_model_trained=False)

    def analyze_live_audio(self, processed_audio: ProcessedAudio) -> LiveAnalysisResult:
        t0_cold = time.perf_counter()

        # 1. Window Slicing
        raw_windows = self.windowing_system.slice_windows(processed_audio)
        if not raw_windows:
            raw_windows = [(0, 0.0, processed_audio.duration_seconds, processed_audio)]

        evaluated_windows: List[LiveWindow] = []
        window_latencies: List[float] = []

        # Single-window predictions
        for idx, start_sec, end_sec, win_audio in raw_windows:
            t0_win = time.perf_counter()
            feats = self.audio_processor.extract_features(win_audio)
            synth_res = self.detector.predict(feats)
            replay_res = self.replay_dsp.analyze_replay_detailed(win_audio)
            risk_res = self.risk_evaluator.evaluate_risk(synth_res, replay_res, win_audio)
            forensic_res = self.forensic_engine.evaluate_forensics(
                synth_res.synthetic_score, replay_res.replay_score, win_audio.audio_signal, win_audio.sample_rate
            )

            win_lat = (time.perf_counter() - t0_win) * 1000.0
            window_latencies.append(win_lat)

            dom_signal = "neural_synthetic" if synth_res.synthetic_score >= 0.50 else "acoustic_replay" if replay_res.replay_score >= 0.50 else "natural_speech"

            evaluated_windows.append(LiveWindow(
                window_index=idx,
                start_time_seconds=start_sec,
                end_time_seconds=end_sec,
                synthetic_score=synth_res.synthetic_score,
                replay_score=replay_res.replay_score,
                risk_score=risk_res.risk_score,
                confidence=forensic_res.confidence_indicator,
                decision=forensic_res.decision,
                dominant_signal=dom_signal
            ))

        t_warm = time.perf_counter()

        # 2. Generalization Artifact Extraction
        gen_artifacts = self.generalization_extractor.extract_artifacts(processed_audio.audio_signal, processed_audio.sample_rate)

        # Overall Detector Contributions
        full_feats = self.audio_processor.extract_features(processed_audio)
        synth_full = self.detector.predict(full_feats)
        replay_full = self.replay_dsp.analyze_replay_detailed(processed_audio)
        forensic_full = self.forensic_engine.evaluate_forensics(
            synth_full.synthetic_score, replay_full.replay_score, processed_audio.audio_signal, processed_audio.sample_rate
        )

        spec_val = 0.5
        temp_val = 0.5
        integ_val = 0.0

        for ev in forensic_full.evidence:
            if ev.get("category") == "SPECTRAL":
                spec_val = float(ev.get("value", 0.5))
            elif ev.get("category") == "TEMPORAL":
                temp_val = float(ev.get("value", 0.5))
            elif ev.get("category") == "INTEGRITY":
                integ_val = float(ev.get("value", 0.0))

        detector_contribs = DetectorContributions(
            neural_score=synth_full.synthetic_score,
            replay_score=replay_full.replay_score,
            spectral_score=spec_val,
            temporal_score=temp_val,
            integrity_score=integ_val,
            generalization_score=gen_artifacts.generalization_risk_score
        )

        # 3. Detector Disagreement Analysis
        agreement_res = self.agreement_engine.analyze_agreement(
            neural_score=synth_full.synthetic_score,
            replay_score=replay_full.replay_score,
            forensic_score=round(forensic_full.risk_score / 100.0, 2),
            generalization_score=gen_artifacts.generalization_risk_score
        )

        # 4. Temporal Multi-Window Evidence Fusion
        stability_res = self.fusion_engine.analyze_temporal_stability(evaluated_windows)
        fused_risk, fused_synth, conf_state, decision = self.fusion_engine.fuse_multi_window_assessment(
            evaluated_windows, stability_res, agreement_res.agreement_state
        )

        if fused_risk >= 75.0:
            risk_level = "CRITICAL"
        elif fused_risk >= 50.0:
            risk_level = "HIGH"
        elif fused_risk >= 30.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        if decision == "LIKELY_SPOOF":
            recommendation = "REJECT — Suspicious synthetic/replay attack indicators detected across temporal analysis windows."
        elif decision == "SUSPICIOUS":
            recommendation = "CHALLENGE — Moderate threat indicators observed; step-up authentication recommended."
        else:
            recommendation = "ACCEPT — Acoustic properties align with authentic natural speech."

        total_lat = round((time.perf_counter() - t0_cold) * 1000.0, 2)
        mean_win_lat = round(float(np.mean(window_latencies)), 2) if window_latencies else 0.0

        proc_meta = {
            "total_duration_ms": total_lat,
            "cold_start_ms": round((t_warm - t0_cold) * 1000.0, 2),
            "mean_window_latency_ms": mean_win_lat,
            "windows_processed": len(evaluated_windows),
            "sample_rate": processed_audio.sample_rate,
            "audio_duration_seconds": processed_audio.duration_seconds
        }

        val_meta = {
            "dataset_status": "DATASET_MISSING",
            "benchmark_status": "BLOCKED",
            "claim_guard_status": "ACTIVE",
            "model_provenance": "DEMO_DSP_SYNTHETIC_DATASET"
        }

        limitations = [
            "Official ASVspoof 2019 LA dataset is missing on local disk; real-world benchmark metrics remain BLOCKED.",
            "Baseline model checkpoint was trained on DSP synthetic demo signals.",
            "Live analysis decisions reflect measured acoustic signal properties rather than official benchmark accuracy."
        ]

        return LiveAnalysisResult(
            status="LIVE_ANALYSIS_COMPLETED",
            decision=decision,
            risk_level=risk_level,
            risk_score=fused_risk,
            confidence_state=conf_state,
            confidence_score=synth_full.confidence,
            detectors=asdict(detector_contribs),
            agreement=asdict(agreement_res),
            temporal_stability=asdict(stability_res),
            windows=[asdict(w) for w in evaluated_windows],
            evidence=forensic_full.evidence,
            counter_evidence=forensic_full.counter_evidence,
            recommendation=recommendation,
            processing_metadata=proc_meta,
            validation_metadata=val_meta,
            limitations=limitations
        )
