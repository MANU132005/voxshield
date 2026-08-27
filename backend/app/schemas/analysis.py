from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal, Dict, Any

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
        description="Overall aggregated risk score [0.0 - 1.0]"
    )
    status: RiskStatus = Field(
        ..., 
        description="Risk category: SAFE, SUSPICIOUS, or HIGH_RISK"
    )
    reasons: List[str] = Field(
        default_factory=list, 
        description="List of human-readable diagnostic reasons"
    )

    # Extended M11 Threat Assessment Fields (Optional)
    risk_level: Optional[str] = Field(
        default=None,
        description="Detailed risk level: LOW, MEDIUM, HIGH, CRITICAL"
    )
    verdict: Optional[str] = Field(
        default=None,
        description="Threat verdict: AUTHENTIC, SUSPICIOUS, SPOOF_SUSPECTED, REPLAY_SUSPECTED, HIGH_RISK"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Assessment confidence magnitude [0.0 - 1.0]"
    )
    evidence: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Structured machine-readable evidence items"
    )
    evaluator_version: Optional[str] = Field(
        default="risk_engine_v1.0",
        description="Risk Evaluator version identifier"
    )

    # Extended M15 Forensic Intelligence Assessment Field (Optional)
    forensics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed multi-vector forensic intelligence assessment object"
    )

    # Extended M16 Explainability & Timeline Fields (Optional)
    explainability: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured decision explainability object with evidence ranking and counter-evidence"
    )
    forensic_timeline: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Forensic analysis execution stage timeline"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "synthetic_score": 0.91,
                "replay_score": 0.73,
                "speaker_match": None,
                "risk_score": 0.89,
                "status": "HIGH_RISK",
                "risk_level": "CRITICAL",
                "verdict": "HIGH_RISK",
                "confidence": 0.87,
                "reasons": [
                    "Synthetic voice characteristics detected",
                    "Possible replay characteristics detected"
                ],
                "evaluator_version": "risk_engine_v1.0"
            }
        }
    )
