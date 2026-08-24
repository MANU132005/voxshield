import os
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.schemas.analysis import AnalysisResponse
from app.services.risk_engine.evaluator import RiskEngine
from app.services.anti_spoofing.detector import AntiSpoofingDetector
from app.services.replay_detection.dsp import ReplayDetector

router = APIRouter()

detector = AntiSpoofingDetector()
replay_dsp = ReplayDetector()
risk_engine = RiskEngine()

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}

@router.post(
    "/analyze", 
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Audio for Voice Impersonation & Replay Attacks"
)
async def analyze_audio(file: UploadFile = File(...)):
    """
    Accepts an uploaded audio file (.wav, .mp3, .flac, .m4a, .ogg) and runs voice
    anti-spoofing and replay attack analysis.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Uploaded file must have a valid filename."
        )

    _, ext = os.path.splitext(file.filename)
    if not ext or ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Unsupported audio format '{ext}'. Allowed formats: .wav, .mp3, .flac, .m4a, .ogg."
        )

    # Read binary content
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Uploaded audio file is empty."
        )

    # Placeholder inference pipeline execution
    # TODO (Developer 1): Replace stub predictions with model tensor inference
    synthetic_prob = detector.predict_synthetic_score(contents)
    replay_prob = replay_dsp.analyze_replay(contents)

    # Compute risk score and status
    result = risk_engine.evaluate(
        synthetic_score=synthetic_prob,
        replay_score=replay_prob
    )

    return result
