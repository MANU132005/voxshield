"""
Bootstrap Confidence Intervals Module.

Computes statistically defensible lower, point estimate, and upper confidence bounds
via deterministic bootstrap resampling over empirical evaluation metric vectors.
"""

from dataclasses import asdict
from typing import Dict, Any, List, Optional
import numpy as np
from app.services.evaluation.types import ConfidenceIntervalResult
from app.services.evaluation.metric_engine import MetricEngine


class BootstrapConfidenceIntervals:
    def __init__(self, metric_engine: MetricEngine = None):
        self.metric_engine = metric_engine or MetricEngine()

    def compute_bootstrap_intervals(
        self,
        labels: np.ndarray,
        scores: np.ndarray,
        confidence_level: float = 0.95,
        bootstrap_count: int = 200,
        seed: int = 42
    ) -> Optional[List[Dict[str, Any]]]:
        if len(labels) == 0 or len(scores) == 0:
            return None

        np.random.seed(seed)
        n = len(labels)
        point_res = self.metric_engine.compute_metrics(labels, scores)

        if point_res.accuracy is None:
            return None

        acc_boot = []
        eer_boot = []

        for _ in range(bootstrap_count):
            indices = np.random.choice(n, size=n, replace=True)
            boot_labels = labels[indices]
            boot_scores = scores[indices]

            res = self.metric_engine.compute_metrics(boot_labels, boot_scores)
            if res.accuracy is not None:
                acc_boot.append(res.accuracy)
            if res.eer is not None:
                eer_boot.append(res.eer)

        alpha = (1.0 - confidence_level) / 2.0
        results = []

        if acc_boot:
            lower = float(np.percentile(acc_boot, alpha * 100))
            upper = float(np.percentile(acc_boot, (1.0 - alpha) * 100))
            results.append(asdict(ConfidenceIntervalResult(
                metric_name="accuracy",
                point_estimate=point_res.accuracy,
                lower_bound=round(lower, 4),
                upper_bound=round(upper, 4),
                confidence_level=confidence_level,
                bootstrap_count=bootstrap_count
            )))

        if eer_boot:
            lower = float(np.percentile(eer_boot, alpha * 100))
            upper = float(np.percentile(eer_boot, (1.0 - alpha) * 100))
            results.append(asdict(ConfidenceIntervalResult(
                metric_name="eer",
                point_estimate=point_res.eer,
                lower_bound=round(lower, 4),
                upper_bound=round(upper, 4),
                confidence_level=confidence_level,
                bootstrap_count=bootstrap_count
            )))

        return results
