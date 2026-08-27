import pytest
from app.services.explainability.counter_evidence import evaluate_counter_evidence


def test_counter_evidence_search_for_likely_spoof():
    evidence_dicts = [
        {"id": "EV1", "category": "SPECTRAL", "signal": "flatness", "explanation": "Low flatness"}
    ]
    counter_evidence_dicts = [
        {"id": "CEV1", "category": "TEMPORAL", "signal": "natural_envelope", "explanation": "Natural speech envelope."}
    ]

    items = evaluate_counter_evidence("LIKELY_SPOOF", evidence_dicts, counter_evidence_dicts)

    assert len(items) >= 1
    assert any("clipping_absent" in i["signal"] for i in items)
    assert any("natural_envelope" in i["signal"] for i in items)


def test_counter_evidence_search_for_likely_genuine():
    evidence_dicts = [
        {"id": "EV1", "category": "SPECTRAL", "signal": "flatness", "explanation": "Subtle flatness anomaly"}
    ]
    counter_evidence_dicts = []

    items = evaluate_counter_evidence("LIKELY_GENUINE", evidence_dicts, counter_evidence_dicts)

    assert len(items) == 1
    assert items[0]["signal"] == "flatness"


def test_counter_evidence_impact_on_confidence():
    items = evaluate_counter_evidence("LIKELY_SPOOF", [], [])
    assert len(items) >= 1
    assert items[0]["impact_on_confidence"] < 0.0
