"""
Forensic Timeline Stage Tracker.

Tracks stages 1-10 of audio analysis execution with execution latencies in milliseconds.
Zero raw audio logging; records stage, status, latency, and warnings.
"""

import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional


@dataclass
class TimelineStage:
    stage_id: int
    stage_name: str
    execution_time_ms: float
    status: str
    warnings: List[str]


class ForensicTimelineTracker:
    def __init__(self):
        self.stages: List[TimelineStage] = []
        self._t0: float = time.perf_counter()

    def record_stage(self, stage_id: int, stage_name: str, status: str = "COMPLETED", warnings: List[str] = None) -> None:
        t_now = time.perf_counter()
        elapsed_ms = round((t_now - self._t0) * 1000.0, 2)
        self._t0 = t_now

        self.stages.append(TimelineStage(
            stage_id=stage_id,
            stage_name=stage_name,
            execution_time_ms=elapsed_ms,
            status=status,
            warnings=warnings or []
        ))

    def get_timeline(self) -> List[Dict[str, Any]]:
        return [asdict(s) for s in self.stages]
