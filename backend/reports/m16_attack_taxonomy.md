# Milestone 16: Expanded Attack Taxonomy Report

**Module**: VoxShield Attack Taxonomy Classifier  
**Date**: 2026-08-25  

---

## 1. Expanded Attack Hypotheses Taxonomy

1. **`AI_SYNTHETIC_VOICE`**: Neural score $\ge 0.65$ or spectral stationarity anomaly.
2. **`VOICE_CONVERSION`**: Spectral/temporal over-regularity without pitch jitter.
3. **`TTS_GENERATION`**: High neural score + zero prosody variation.
4. **`REPLAY_ATTACK` / `RECORDING_REPLAY`**: Single-STFT replay score $\ge 0.50$ or high-frequency attenuation.
5. **`VOCODER_ARTIFACT`**: Abnormally low spectral flatness or frame-to-frame stationarity.
6. **`SIGNAL_MANIPULATION`**: Hard clipping or DC offset bias.
7. **`CLIPPED_RECORDING`**: Clipping ratio $> 1.0\%$.
8. **`HEAVY_COMPRESSION`**: Abnormally low crest factor ($< 6.0\text{ dB}$).
9. **`ENVIRONMENTAL_RECORDING`**: High noise floor ($> -30\text{ dB}$).
10. **`NO_STRONG_SPOOF_EVIDENCE`**: Natural acoustic alignment.
