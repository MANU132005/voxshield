import pytest
from app.services.explainability.decision_explainer import DecisionExplainer
from app.services.explainability.evidence_ranker import rank_evidence_items
from app.services.explainability.explanation_builder import build_explanation_text


@pytest.fixture
def explainer():
    return DecisionExplainer()


def test_evidence_ranking_deterministic_order():
    ev_items = [
        {"id": "EV1", "category": "SPECTRAL", "signal": "flatness", "normalized_strength": 0.5, "reliability": 0.8},
        {"id": "EV2", "category": "NEURAL", "signal": "synthetic", "normalized_strength": 0.9, "reliability": 0.9},
        {"id": "EV3", "category": "INTEGRITY", "signal": "clipping", "normalized_strength": 0.7, "reliability": 0.85}
    ]

    ranked = rank_evidence_items(ev_items)

    assert len(ranked) == 3
    assert ranked[0]["evidence_id"] == "EV2"  # 0.9 * 0.9 = 0.81 (Highest)
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2
    assert ranked[2]["rank"] == 3


def test_decision_explainer_high_confidence(explainer):
    ev = [{"id": "EV1", "category": "SPECTRAL", "signal": "flatness", "normalized_strength": 0.8, "reliability": 0.9, "explanation": "Low flatness"}]
    lims = ["ASVspoof dataset missing"]

    res = explainer.explain_decision(
        decision="LIKELY_SPOOF",
        risk_score=85.0,
        confidence_indicator=0.85,
        evidence_dicts=ev,
        counter_evidence_dicts=[],
        limitations=lims
    )

    assert res.decision == "LIKELY_SPOOF"
    assert res.confidence_state == "HIGH_MEASUREMENT_CONFIDENCE"
    assert len(res.primary_evidence) == 1
    assert "ASVspoof" in res.limitations[0]


def test_decision_explainer_low_confidence(explainer):
    res = explainer.explain_decision(
        decision="INCONCLUSIVE",
        risk_score=20.0,
        confidence_indicator=0.30,
        evidence_dicts=[],
        counter_evidence_dicts=[],
        limitations=[]
    )

    assert res.confidence_state == "INSUFFICIENT_EVIDENCE"


def test_explanation_text_builder(explainer):
    ev = [{"id": "EV1", "category": "SPECTRAL", "signal": "flatness", "normalized_strength": 0.8, "reliability": 0.9, "explanation": "Low flatness"}]
    res = explainer.explain_decision(
        decision="LIKELY_SPOOF",
        risk_score=85.0,
        confidence_indicator=0.85,
        evidence_dicts=ev,
        counter_evidence_dicts=[],
        limitations=["Demo model provenance"]
    )

    text = build_explanation_text(res)
    assert "VOXSHIELD DECISION EXPLAINABILITY REPORT" in text
    assert "LIKELY_SPOOF" in text
    assert "HIGH_MEASUREMENT_CONFIDENCE" in text


def test_no_explanation_hallucination(explainer):
    res = explainer.explain_decision(
        decision="LIKELY_GENUINE",
        risk_score=10.0,
        confidence_indicator=0.90,
        evidence_dicts=[],
        counter_evidence_dicts=[],
        limitations=[]
    )

    assert len(res.primary_evidence) == 0
    assert len(res.counter_evidence) == 0
