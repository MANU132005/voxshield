# Milestone 16: Decision Explainability & Counter-Evidence Report

**Module**: VoxShield Decision Explainer & Evidence Ranker  
**Date**: 2026-08-25  

---

## 1. Overview & Architecture

The **Decision Explainer** (`app/services/explainability/`) converts raw detection scores into structured human-readable explanations. It incorporates:
1. **Deterministic Evidence Ranking**: Ranks evidence items by $S_{\text{evidence}} = \text{strength} \times \text{reliability}$.
2. **Active Counter-Evidence Search**: Searches for clean natural acoustic properties to challenge a tentative `LIKELY_SPOOF` decision and prevent confirmation bias.
3. **Explicit Confidence States**: Replaces generic probabilities with `HIGH_MEASUREMENT_CONFIDENCE`, `MODERATE_MEASUREMENT_CONFIDENCE`, `LOW_MEASUREMENT_CONFIDENCE`, or `INSUFFICIENT_EVIDENCE`.

---

## 2. Zero-Hallucination Evidence Rule
Every explanation item maps directly to a measured or inferred signal metric (`EvidenceItem`). No static generic statements are generated.
