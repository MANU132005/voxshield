"""
In-Memory Streaming Live Session Manager with TTL Eviction.
"""

import time
import uuid
import numpy as np
from dataclasses import asdict
from typing import Dict, Any, Optional, Tuple
from app.services.live_detection.types import LiveSessionState


class LiveSessionManager:
    def __init__(self, session_ttl_seconds: float = 300.0):
        self.session_ttl_seconds = session_ttl_seconds
        self._sessions: Dict[str, LiveSessionState] = {}
        self._audio_buffers: Dict[str, List[np.ndarray]] = {}

    def create_session(self, sample_rate: int = 16000) -> LiveSessionState:
        self._cleanup_expired_sessions()
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        state = LiveSessionState(
            session_id=session_id,
            sample_rate=sample_rate
        )
        self._sessions[session_id] = state
        self._audio_buffers[session_id] = []
        return state

    def get_session(self, session_id: str) -> Optional[LiveSessionState]:
        self._cleanup_expired_sessions()
        return self._sessions.get(session_id)

    def add_chunk(self, session_id: str, pcm_signal: np.ndarray) -> Optional[LiveSessionState]:
        self._cleanup_expired_sessions()
        state = self._sessions.get(session_id)
        if not state or state.is_finalized:
            return None

        self._audio_buffers[session_id].append(pcm_signal.astype(np.float32))
        state.chunks_received += 1
        state.accumulated_samples += len(pcm_signal)
        state.total_duration_seconds = round(state.accumulated_samples / float(state.sample_rate), 4)
        state.updated_at = time.time()
        return state

    def finalize_session(self, session_id: str) -> Tuple[Optional[LiveSessionState], Optional[np.ndarray]]:
        self._cleanup_expired_sessions()
        state = self._sessions.get(session_id)
        if not state:
            return None, None

        state.is_finalized = True
        state.updated_at = time.time()

        chunks = self._audio_buffers.get(session_id, [])
        if chunks:
            full_signal = np.concatenate(chunks, axis=0)
        else:
            full_signal = np.zeros(0, dtype=np.float32)

        return state, full_signal

    def _cleanup_expired_sessions(self):
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if (now - s.updated_at) > self.session_ttl_seconds]
        for sid in expired:
            self._sessions.pop(sid, None)
            self._audio_buffers.pop(sid, None)
