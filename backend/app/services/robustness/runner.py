"""
Phase 4 Robustness Evaluation Runner Module.

Executes baseline vs transformed audio evaluations across all 7 robustness conditions,
computing delta metrics and measuring performance overhead.
"""

import time
from dataclasses import asdict
from typing import Dict, Any, List
import numpy as np

from app.services.audio.processor import AudioProcessor, ProcessedAudio
from app.services.anti_spoofing.detector import AntiSpoofingDetector
from app.services.replay_detection.dsp import ReplayDetector
from app.services.risk_engine.evaluator import RiskEvaluator
from app.services.forensics.forensic_engine import ForensicEngine

from app.services.robustness.types import (
    RobustnessCondition,
    RobustnessConditionType,
    ComparisonDelta,
    RobustnessResult,
    RobustnessAssessment
)
from app.services.robustness.transformations import (
    apply_replay_transformation,
    apply_noise_transformation,
    apply_reverberation_transformation,
    apply_compression_transformation,
    apply_clipping_transformation,
    apply_synthetic_variation_transformation,
    apply_controlled_perturbation_transformation
)


class RobustnessRunner:
    def __init__(
        self,
        audio_processor: AudioProcessor = None,
        detector: AntiSpoofingDetector = None,
        replay_dsp: ReplayDetector = None,
        risk_evaluator: RiskEvaluator = None,
        forensic_engine: ForensicEngine = None
    ):
        self.audio_processor = audio_processor or AudioProcessor()
        self.detector = detector or AntiSpoofingDetector()
        self.replay_dsp = replay_dsp or ReplayDetector()
        self.risk_evaluator = risk_evaluator or RiskEvaluator()
        self.forensic_engine = forensic_engine or ForensicEngine()

    def evaluate_condition(
        self,
        processed_audio: ProcessedAudio,
        condition: RobustnessCondition
    ) -> RobustnessResult:
        # 1. Baseline Evaluation
        t0_base = time.perf_counter()
        feats_base = self.audio_processor.extract_features(processed_audio)
        synth_base = self.detector.predict(feats_base)
        replay_base = self.replay_dsp.analyze_replay_detailed(processed_audio)
        risk_base = self.risk_evaluator.evaluate_risk(synth_base, replay_base, processed_audio)
        forensic_base = self.forensic_engine.evaluate_forensics(
            synth_base.synthetic_score, replay_base.replay_score, processed_audio.audio_signal, processed_audio.sample_rate
        )
        base_latency = (time.perf_counter() - t0_base) * 1000.0

        # 2. Audio Transformation
        t0_trans = time.perf_counter()
        c_type = condition.condition_type

        if c_type == RobustnessConditionType.REPLAY.value:
            trans_signal = apply_replay_transformation(processed_audio.audio_signal, processed_audio.sample_rate, condition.severity)
        elif c_type == RobustnessConditionType.NOISE.value:
            snr = condition.parameters.get("snr_db", 20.0)
            trans_signal = apply_noise_transformation(processed_audio.audio_signal, snr_db=snr)
        elif c_type == RobustnessConditionType.REVERBERATION.value:
            decay = condition.parameters.get("decay", 0.5)
            trans_signal = apply_reverberation_transformation(processed_audio.audio_signal, processed_audio.sample_rate, decay=decay)
        elif c_type == RobustnessConditionType.COMPRESSION.value:
            target_sr = condition.parameters.get("target_sr", 8000)
            trans_signal = apply_compression_transformation(processed_audio.audio_signal, processed_audio.sample_rate, target_sr=target_sr)
        elif c_type == RobustnessConditionType.CLIPPING.value:
            thresh = condition.parameters.get("threshold", 0.70)
            trans_signal = apply_clipping_transformation(processed_audio.audio_signal, threshold=thresh)
        elif c_type == RobustnessConditionType.SYNTHETIC_VARIATION.value:
            trans_signal, _ = apply_synthetic_variation_transformation(processed_audio.audio_signal)
        elif c_type == RobustnessConditionType.PERTURBATION.value:
            amp = condition.parameters.get("pert_amp", 0.02)
            trans_signal = apply_controlled_perturbation_transformation(processed_audio.audio_signal, pert_amp=amp)
        else:
            trans_signal = processed_audio.audio_signal.copy()

        trans_latency = (time.perf_counter() - t0_trans) * 1000.0

        # 3. Transformed Audio Container
        peak_amp = float(np.max(np.abs(trans_signal))) if len(trans_signal) > 0 else 0.0
        trans_audio = ProcessedAudio(
            audio_signal=trans_signal,
            sample_rate=processed_audio.sample_rate,
            duration_seconds=processed_audio.duration_seconds,
            channels=1,
            original_sample_rate=processed_audio.original_sample_rate,
            original_channels=processed_audio.original_channels,
            peak_amplitude=round(peak_amp, 5)
        )

        # 4. Transformed Evaluation
        t0_trans_eval = time.perf_counter()
        feats_trans = self.audio_processor.extract_features(trans_audio)
        synth_trans = self.detector.predict(feats_trans)
        replay_trans = self.replay_dsp.analyze_replay_detailed(trans_audio)
        risk_trans = self.risk_evaluator.evaluate_risk(synth_trans, replay_trans, trans_audio)
        forensic_trans = self.forensic_engine.evaluate_forensics(
            synth_trans.synthetic_score, replay_trans.replay_score, trans_audio.audio_signal, trans_audio.sample_rate
        )
        trans_eval_latency = (time.perf_counter() - t0_trans_eval) * 1000.0

        # 5. Compute Comparison Delta
        synth_delta = round(synth_trans.synthetic_score - synth_base.synthetic_score, 4)
        replay_delta = round(replay_trans.replay_score - replay_base.replay_score, 4)
        risk_delta = round(risk_trans.risk_score - risk_base.risk_score, 2)
        conf_delta = round(forensic_trans.confidence_indicator - forensic_base.confidence_indicator, 4)

        decision_changed = (forensic_base.decision != forensic_trans.decision)

        delta = ComparisonDelta(
            synthetic_score_delta=synth_delta,
            replay_score_delta=replay_delta,
            risk_score_delta=risk_delta,
            confidence_delta=conf_delta,
            decision_before=forensic_base.decision,
            decision_after=forensic_trans.decision,
            decision_changed=decision_changed,
            evidence_added_count=max(0, len(forensic_trans.evidence) - len(forensic_base.evidence)),
            evidence_removed_count=max(0, len(forensic_base.evidence) - len(forensic_trans.evidence))
        )

        total_lat = round(base_latency + trans_latency + trans_eval_latency, 2)

        return RobustnessResult(
            condition_id=condition.condition_id,
            condition_type=condition.condition_type,
            severity=condition.severity,
            parameters=condition.parameters,
            source_audio_id=condition.source_audio_id,
            baseline_synthetic_score=synth_base.synthetic_score,
            transformed_synthetic_score=synth_trans.synthetic_score,
            baseline_replay_score=replay_base.replay_score,
            transformed_replay_score=replay_trans.replay_score,
            baseline_risk_score=risk_base.risk_score,
            transformed_risk_score=risk_trans.risk_score,
            baseline_confidence=forensic_base.confidence_indicator,
            transformed_confidence=forensic_trans.confidence_indicator,
            baseline_decision=forensic_base.decision,
            transformed_decision=forensic_trans.decision,
            delta=delta,
            baseline_latency_ms=round(base_latency, 2),
            transformed_latency_ms=round(trans_eval_latency, 2),
            transformation_latency_ms=round(trans_latency, 2),
            total_latency_ms=total_lat
        )

    def run_standard_suite(self, processed_audio: ProcessedAudio) -> RobustnessAssessment:
        conditions = [
            RobustnessCondition("RC_01_REPLAY", RobustnessConditionType.REPLAY.value, "MEDIUM", {}, "AUDIO_01", "Simulated microphonic replay response"),
            RobustnessCondition("RC_02_NOISE_20DB", RobustnessConditionType.NOISE.value, "LOW", {"snr_db": 20.0}, "AUDIO_01", "Additive SNR 20dB background noise"),
            RobustnessCondition("RC_03_REVERB", RobustnessConditionType.REVERBERATION.value, "MEDIUM", {"decay": 0.5}, "AUDIO_01", "Synthetic RIR decay reverberation"),
            RobustnessCondition("RC_04_CODEC_8KHZ", RobustnessConditionType.COMPRESSION.value, "MEDIUM", {"target_sr": 8000}, "AUDIO_01", "Codec resampling quality degradation"),
            RobustnessCondition("RC_05_CLIPPING_07", RobustnessConditionType.CLIPPING.value, "HIGH", {"threshold": 0.70}, "AUDIO_01", "Amplitude hard clipping saturation"),
            RobustnessCondition("RC_06_SYNTH_VAR", RobustnessConditionType.SYNTHETIC_VARIATION.value, "MEDIUM", {}, "AUDIO_01", "Synthetic voice pitch variation fixture"),
            RobustnessCondition("RC_07_PERTURBATION", RobustnessConditionType.PERTURBATION.value, "LOW", {"pert_amp": 0.02}, "AUDIO_01", "Controlled low-level non-destructive perturbation")
        ]

        results: List[Dict[str, Any]] = []
        stable_count = 0
        total_trans_lat = 0.0

        for cond in conditions:
            res = self.evaluate_condition(processed_audio, cond)
            if not res.delta.decision_changed:
                stable_count += 1
            total_trans_lat += res.transformation_latency_ms
            results.append(asdict(res))

        stability_ratio = round(stable_count / max(len(conditions), 1), 4)
        mean_trans_lat = round(total_trans_lat / max(len(conditions), 1), 2)

        disclosures = [
            "Phase 4 robustness testing evaluates controlled attack and degradation conditions. It does not constitute ASVspoof benchmark certification.",
            "Real ASVspoof 2019 LA benchmark metrics remain BLOCKED until the official dataset is available and successfully evaluated."
        ]

        return RobustnessAssessment(
            overall_status="ROBUSTNESS_ENGINE_VERIFIED",
            conditions_evaluated=len(conditions),
            conditions_stable_count=stable_count,
            stability_ratio=stability_ratio,
            mean_transformation_latency_ms=mean_trans_lat,
            results=results,
            disclosures=disclosures
        )
