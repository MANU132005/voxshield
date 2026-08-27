import pytest
import numpy as np
from app.services.evaluation.calibration import ModelScoreCalibration
from app.services.evaluation.types import CalibrationStatus


def test_missing_calibration_dataset_returns_blocked():
    cal = ModelScoreCalibration()
    res = cal.evaluate_calibration_status(calibration_dataset_present=False)

    assert res["status"] == CalibrationStatus.CALIBRATION_BLOCKED.value
    assert res["sample_count"] == 0
    assert res["brier_score"] is None


def test_valid_calibration_evaluates_brier_score():
    cal = ModelScoreCalibration()
    scores = np.array([0.1, 0.9])
    labels = np.array([0, 1])

    res = cal.evaluate_calibration_status(calibration_dataset_present=True, scores=scores, labels=labels)

    assert res["status"] == CalibrationStatus.CALIBRATED.value
    assert res["sample_count"] == 2
    assert res["brier_score"] == 0.01
