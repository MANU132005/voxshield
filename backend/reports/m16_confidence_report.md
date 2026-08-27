# Milestone 16: Confidence Calibration Guard Report

**Module**: VoxShield Confidence Calibration Guard  
**Date**: 2026-08-25  

---

## 1. Overview & Confidence Taxonomy

The Confidence Calibration Guard assigns explicit confidence states based on empirical signal factors:

```text
Confidence States
├── HIGH_MEASUREMENT_CONFIDENCE     (indicator >= 0.80)
├── MODERATE_MEASUREMENT_CONFIDENCE (indicator >= 0.60)
├── LOW_MEASUREMENT_CONFIDENCE      (indicator >= 0.40)
└── INSUFFICIENT_EVIDENCE           (indicator < 0.40)
```

---

## 2. Confidence Assignment Criteria
1. **Audio Duration**: Duration $< 0.8\text{s}$ applies a $-0.20$ penalty.
2. **Provenance Disclosure**: Demo synthetic model checkpoint applies a $-0.15$ penalty.
3. **Cross-Signal Agreement**: Unanimous spoof evidence applies a $+0.05$ bonus; contradictory evidence applies a $-0.10$ penalty.
