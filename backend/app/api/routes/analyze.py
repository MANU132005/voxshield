import os
from dataclasses import asdict
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.schemas.analysis import AnalysisResponse
from app.services.audio.processor import AudioProcessor, AudioProcessingError
from app.services.anti_spoofing.detector import AntiSpoofingDetector
from app.services.replay_detection.dsp import ReplayDetector
from app.services.risk_engine.evaluator import RiskEvaluator
from app.services.forensics.forensic_engine import ForensicEngine
from app.services.forensics.timeline import ForensicTimelineTracker
from app.services.explainability.decision_explainer import DecisionExplainer
from app.core.config import settings

router = APIRouter()

audio_processor = AudioProcessor(
    target_sample_rate=16000,
    min_duration_seconds=settings.MIN_AUDIO_DURATION_SECONDS
)
detector = AntiSpoofingDetector()
replay_dsp = ReplayDetector()
risk_evaluator = RiskEvaluator()
forensic_engine = ForensicEngine()
decision_explainer = DecisionExplainer()

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
MAX_FILE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post(
    "/analyze", 
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Audio for Voice Impersonation & Replay Attacks",
    responses={
        200: {"description": "Successful multi-modal threat analysis"},
        400: {"description": "Bad Request - Empty file or invalid audio structure"},
        413: {"description": "Payload Too Large - Upload size exceeds limit (15 MB)"},
        415: {"description": "Unsupported Media Type - Audio format not supported"},
        429: {"description": "Too Many Requests - Rate limit exceeded"}
    }
)
async def analyze_audio(file: UploadFile = File(...)):
    """
    Accepts an uploaded audio file (.wav, .mp3, .flac, .m4a, .ogg) and runs voice
    anti-spoofing, acoustic replay attack analysis, multi-modal risk evaluation, forensic intelligence analysis, and decision explainability.
    """
    timeline = ForensicTimelineTracker()
    timeline.record_stage(1, "Audio Payload Received")

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Uploaded file must have a valid filename."
        )

    # Sanitize filename (prevent path traversal attempts in filename)
    safe_filename = os.path.basename(file.filename)
    if len(safe_filename) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename length exceeds maximum limit of 255 characters."
        )

    _, ext = os.path.splitext(safe_filename)
    if not ext or ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Unsupported audio format '{ext}'. Allowed formats: .wav, .mp3, .flac, .m4a, .ogg."
        )

    timeline.record_stage(2, "Filename & Format Validation")

    # Read binary content securely
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Uploaded audio file is empty."
        )

    if len(contents) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum upload limit of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    timeline.record_stage(3, "Upload Security Verification")

    # Audio preprocessing pipeline (Decode, Mono, 16kHz, Peak Normalize, Quality Checks)
    try:
        processed_audio = audio_processor.load_and_preprocess(contents, safe_filename)
        timeline.record_stage(4, "Audio Normalization & Resampling")
        features = audio_processor.extract_features(processed_audio)
        timeline.record_stage(5, "Spectrogram & Feature Extraction")
    except AudioProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Execute AI anti-spoofing neural inference and DSP acoustic replay analysis
    synthetic_result = detector.predict(features)
    timeline.record_stage(6, "Neural Anti-Spoofing Inference")

    replay_result = replay_dsp.analyze_replay_detailed(processed_audio)
    timeline.record_stage(7, "Acoustic Replay DSP Analysis")

    # Execute multi-modal threat risk assessment
    assessment = risk_evaluator.evaluate_risk(
        synthetic_input=synthetic_result,
        replay_input=replay_result,
        processed_audio=processed_audio
    )
    timeline.record_stage(8, "Multi-Signal Threat Risk Assessment")

    # Execute Forensic Intelligence Analysis
    forensic_assessment = forensic_engine.evaluate_forensics(
        synthetic_score=synthetic_result.synthetic_score,
        replay_score=replay_result.replay_score,
        signal=processed_audio.audio_signal,
        sample_rate=processed_audio.sample_rate
    )
    timeline.record_stage(9, "Forensic Intelligence Analysis")

    # Compute Decision Explanation
    explanation = decision_explainer.explain_decision(
        decision=forensic_assessment.decision,
        risk_score=forensic_assessment.risk_score,
        confidence_indicator=forensic_assessment.confidence_indicator,
        evidence_dicts=forensic_assessment.evidence,
        counter_evidence_dicts=forensic_assessment.counter_evidence,
        limitations=forensic_assessment.limitations,
        claim_status=forensic_assessment.claim_status
    )
    timeline.record_stage(10, "Decision Explainability & Final Response Assembly")

    # Legacy risk score mapping for API response compatibility [0.0 - 1.0]
    legacy_risk_score = round(assessment.risk_score / 100.0, 2)
    if legacy_risk_score >= 0.70:
        legacy_status = "HIGH_RISK"
    elif legacy_risk_score >= 0.35:
        legacy_status = "SUSPICIOUS"
    else:
        legacy_status = "SAFE"

    return AnalysisResponse(
        synthetic_score=round(synthetic_result.synthetic_score, 2),
        replay_score=round(replay_result.replay_score, 2),
        speaker_match=None,
        risk_score=legacy_risk_score,
        status=legacy_status,
        reasons=assessment.reasons,
        risk_level=assessment.risk_level,
        verdict=assessment.verdict,
        confidence=assessment.confidence,
        evidence=assessment.evidence,
        evaluator_version=assessment.evaluator_version,
        forensics=asdict(forensic_assessment),
        explainability=asdict(explanation),
        forensic_timeline=timeline.get_timeline()
    )
