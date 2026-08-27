"""
Metric Engine Module.

Computes Accuracy, Precision, Recall, F1, ROC-AUC, EER with linear threshold interpolation,
FAR, FRR, and confusion matrices when real evaluation dataset is present. Handles edge cases
(empty labels, single-class targets, NaN scores) gracefully.
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
import scipy.integrate
from app.services.evaluation.types import MetricResult
from scripts.evaluate_real_world import calculate_eer


class MetricEngine:
    def compute_metrics(self, labels: np.ndarray, scores: np.ndarray, threshold: float = 0.5) -> MetricResult:
        if len(labels) == 0 or len(scores) == 0:
            return MetricResult(
                accuracy=None, precision=None, recall=None, f1_score=None,
                roc_auc=None, eer=None, eer_threshold=None, far=None, frr=None,
                confusion_matrix=None, sample_count=0
            )

        labels = np.array(labels)
        scores = np.array(scores)

        # NaN / Inf filtering
        valid_mask = np.isfinite(labels) & np.isfinite(scores)
        labels = labels[valid_mask].astype(int)
        scores = scores[valid_mask].astype(np.float32)

        if len(labels) == 0:
            return MetricResult(
                accuracy=None, precision=None, recall=None, f1_score=None,
                roc_auc=None, eer=None, eer_threshold=None, far=None, frr=None,
                confusion_matrix=None, sample_count=0
            )

        preds = (scores >= threshold).astype(int)

        tp = int(np.sum((preds == 1) & (labels == 1)))
        tn = int(np.sum((preds == 0) & (labels == 0)))
        fp = int(np.sum((preds == 1) & (labels == 0)))
        fn = int(np.sum((preds == 0) & (labels == 1)))

        acc = float((tp + tn) / max(len(labels), 1))
        prec = float(tp / max(tp + fp, 1))
        rec = float(tp / max(tp + fn, 1))
        f1 = float(2 * prec * rec / max(prec + rec, 1e-7))

        far = float(fp / max(fp + tn, 1))
        frr = float(fn / max(fn + tp, 1))

        eer, eer_thresh = calculate_eer(labels, scores)

        # ROC-AUC calculation
        roc_auc = self._calculate_roc_auc(labels, scores)

        return MetricResult(
            accuracy=round(acc, 4),
            precision=round(prec, 4),
            recall=round(rec, 4),
            f1_score=round(f1, 4),
            roc_auc=round(roc_auc, 4) if roc_auc is not None else None,
            eer=eer,
            eer_threshold=eer_thresh,
            far=round(far, 4),
            frr=round(frr, 4),
            confusion_matrix={"tp": tp, "tn": tn, "fp": fp, "fn": fn},
            sample_count=len(labels)
        )

    def _calculate_roc_auc(self, labels: np.ndarray, scores: np.ndarray) -> Optional[float]:
        if len(np.unique(labels)) < 2:
            return None

        # Trapezoidal ROC-AUC calculation
        thresholds = np.linspace(0.0, 1.0, 501)
        tpr_list = []
        fpr_list = []

        pos_count = np.sum(labels == 1)
        neg_count = np.sum(labels == 0)

        for t in thresholds:
            tp = np.sum((scores >= t) & (labels == 1))
            fp = np.sum((scores >= t) & (labels == 0))
            tpr_list.append(tp / pos_count)
            fpr_list.append(fp / neg_count)

        # Integrate curve via trapezoidal rule
        fpr_arr = np.array(fpr_list)[::-1]
        tpr_arr = np.array(tpr_list)[::-1]
        
        # Compatibility with numpy 2.0 / scipy
        if hasattr(scipy.integrate, "trapezoid"):
            auc = float(scipy.integrate.trapezoid(tpr_arr, fpr_arr))
        elif hasattr(np, "trapezoid"):
            auc = float(np.trapezoid(tpr_arr, fpr_arr))
        else:
            auc = float(np.trapz(tpr_arr, fpr_arr))

        return float(np.clip(auc, 0.0, 1.0))
