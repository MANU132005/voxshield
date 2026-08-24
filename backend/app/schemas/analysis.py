from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal

RiskStatus = Literal["SAFE", "SUSPICIOUS", "HIGH_RISK"]

class AnalysisResponse(BaseModel):
    synthetic_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Probability score of voice being AI generated or cloned"
    )
    replay_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Probability score of audio replay/playback attack"
    )
    speaker_match: Optional[float] = Field(
        default=None, 
        description="Biometric speaker match percentage. Initially null until Phase 2 speaker verification."
    )
    risk_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Overall aggregated risk score"
    )
    status: RiskStatus = Field(
        ..., 
        description="Risk category: SAFE, SUSPICIOUS, or HIGH_RISK"
    )
    reasons: List[str] = Field(
        default_factory=list, 
        description="List of human-readable diagnostic reasons"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "synthetic_score": 0.91,
                "replay_score": 0.73,
                "speaker_match": None,
                "risk_score": 0.89,
                "status": "HIGH_RISK",
                "reasons": [
                    "Synthetic voice characteristics detected",
                    "Possible replay characteristics detected"
                ]
            }
        }
    )

