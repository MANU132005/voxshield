import os
import numpy as np
from dataclasses import asdict
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.services.audio.processor import AudioProcessor, AudioProcessingError
from app.services.live_detection.live_engine import LiveDetectionEngine
from app.services.live_detection.session_manager import LiveSessionManager
from app.core.config import settings

router = APIRouter()

audio_processor = AudioProcessor(
    target_sample_rate=16000,
    min_duration_seconds=settings.MIN_AUDIO_DURATION_SECONDS
)
live_engine = LiveDetectionEngine(audio_processor=audio_processor)
session_manager = LiveSessionManager()

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
MAX_FILE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK,
    summary="Live Windowed Audio Deepfake & Replay Analysis"
)
async def analyze_live_audio(file: UploadFile = File(...)):
    """Accepts uploaded audio and runs multi-window temporal live detection."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a valid filename.")

    safe_filename = os.path.basename(file.filename)
    if len(safe_filename) > 255:
        raise HTTPException(status_code=400, detail="Filename exceeds 255 characters limit.")

    _, ext = os.path.splitext(safe_filename)
    if not ext or ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    if len(contents) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail=f"File size exceeds limit of {settings.MAX_UPLOAD_SIZE_MB} MB.")

    try:
        processed_audio = audio_processor.load_and_preprocess(contents, safe_filename)
    except AudioProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

    res = live_engine.analyze_live_audio(processed_audio)
    return asdict(res)


@router.post(
    "/session",
    status_code=status.HTTP_201_CREATED,
    summary="Create Live Streaming Session"
)
async def create_live_session():
    """Initializes a new streaming session state for chunked live audio ingestion."""
    state = session_manager.create_session()
    return asdict(state)


@router.post(
    "/session/{session_id}/chunk",
    status_code=status.HTTP_200_OK,
    summary="Append Live Audio Chunk to Session"
)
async def append_session_chunk(session_id: str, file: UploadFile = File(...)):
    """Appends an audio chunk to an active live streaming session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Live session '{session_id}' not found or expired.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded chunk is empty.")

    try:
        processed = audio_processor.load_and_preprocess(contents, "chunk.wav")
    except AudioProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

    updated_state = session_manager.add_chunk(session_id, processed.audio_signal)
    if not updated_state:
        raise HTTPException(status_code=400, detail="Session finalized or inactive.")

    return asdict(updated_state)


@router.post(
    "/session/{session_id}/finalize",
    status_code=status.HTTP_200_OK,
    summary="Finalize Session and Execute Live Fusion Analysis"
)
async def finalize_session(session_id: str):
    """Finalizes streaming session and returns multi-window temporal fusion assessment."""
    state, full_signal = session_manager.finalize_session(session_id)
    if not state or full_signal is None or len(full_signal) == 0:
        raise HTTPException(status_code=400, detail=f"Session '{session_id}' has no accumulated audio chunks.")

    from app.services.audio.processor import ProcessedAudio
    peak_amp = float(np.max(np.abs(full_signal))) if len(full_signal) > 0 else 0.0
    full_audio = ProcessedAudio(
        audio_signal=full_signal,
        sample_rate=state.sample_rate,
        duration_seconds=round(len(full_signal) / float(state.sample_rate), 4),
        channels=1,
        original_sample_rate=state.sample_rate,
        original_channels=1,
        peak_amplitude=round(peak_amp, 5)
    )

    res = live_engine.analyze_live_audio(full_audio)
    state.latest_assessment = asdict(res)
    return asdict(res)


@router.get(
    "/session/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Live Session Metadata State"
)
async def get_session_state(session_id: str):
    """Retrieves live session state and metadata."""
    state = session_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Live session '{session_id}' not found.")
    return asdict(state)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Live Detection Engine Health Probe"
)
async def live_health_probe():
    """Health check endpoint for live detection engine."""
    return {
        "status": "HEALTHY",
        "live_engine": "READY",
        "benchmark_status": "BLOCKED",
        "claim_guard": "ACTIVE"
    }
