import pytest
import numpy as np
from app.services.evaluation.metric_engine import MetricEngine
from app.services.evaluation.confidence_intervals import BootstrapConfidenceIntervals


def test_metric_engine_perfect_classification():
    engine = MetricEngine()
    labels = np.array([0, 0, 0, 1, 1, 1])
    scores = np.array([0.1, 0.2, 0.15, 0.85, 0.9, 0.95])

    res = engine.compute_metrics(labels, scores)

    assert res.accuracy == 1.0
    assert res.precision == 1.0
    assert res.recall == 1.0
    assert res.f1_score == 1.0
    assert res.eer == 0.0
    assert res.roc_auc == 1.0


def test_metric_engine_empty_input_returns_none():
    engine = MetricEngine()
    res = engine.compute_metrics(np.array([]), np.array([]))

    assert res.accuracy is None
    assert res.sample_count == 0


def test_metric_engine_nan_filtering():
    engine = MetricEngine()
    labels = np.array([0, 1, np.nan])
    scores = np.array([0.2, 0.8, np.nan])

    res = engine.compute_metrics(labels, scores)

    assert res.sample_count == 2
    assert res.accuracy == 1.0


def test_bootstrap_confidence_intervals():
    ci_engine = BootstrapConfidenceIntervals()
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    scores = np.array([0.1, 0.2, 0.15, 0.05, 0.85, 0.9, 0.95, 0.8])

    res = ci_engine.compute_bootstrap_intervals(labels, scores, bootstrap_count=50)

    assert res is not None
    assert len(res) >= 1
    assert res[0]["metric_name"] == "accuracy"
    assert res[0]["lower_bound"] <= res[0]["point_estimate"] <= res[0]["upper_bound"]
