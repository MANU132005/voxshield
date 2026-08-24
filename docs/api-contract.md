# VoxShield API Contract Specification (v1)

This specification defines the RESTful and WebSocket API contract between the VoxShield Frontend (React) and Backend (FastAPI).

---

## Base URL
`http://localhost:8000/api/v1`

---

## Endpoints

### 1. Health Check
Checks backend service availability and model load status.

- **URL**: `/health`
- **Method**: `GET`
- **Headers**: `Accept: application/json`

#### Response (200 OK):
```json
{
  "status": "ok"
}
```

---

### 2. Audio Deepfake Analysis
Analyzes an uploaded audio sample for synthetic generation markers and acoustic replay artifacts.

- **URL**: `/analyze`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

#### Request Parameters:
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file` | `UploadFile` (Binary) | Yes | Audio file (.wav, .mp3, .flac, .m4a) |

#### Response (200 OK):
```json
{
  "synthetic_score": 0.91,
  "replay_score": 0.73,
  "speaker_match": null,
  "risk_score": 0.89,
  "status": "HIGH_RISK",
  "reasons": [
    "Synthetic voice characteristics detected",
    "Possible replay characteristics detected"
  ]
}
```

#### Response Fields:
- `synthetic_score` (`float` [0.0 - 1.0]): Probability that voice is AI generated/cloned.
- `replay_score` (`float` [0.0 - 1.0]): Probability of physical speaker playback/reverberation.
- `speaker_match` (`float` or `null`): Biometric speaker match percentage. *Must be `null` in Phase 1.*
- `risk_score` (`float` [0.0 - 1.0]): Aggregated threat score.
- `status` (`enum`): `SAFE` | `SUSPICIOUS` | `HIGH_RISK`
- `reasons` (`string[]`): Array of human-readable diagnostic explanations.

#### Error Responses:
- `400 Bad Request`: Unsupported audio format or empty file payload.
- `500 Internal Server Error`: DSP/Model processing failure.

---

### 3. Real-Time WebSocket Audio Stream (Placeholder)
Establishes a WebSocket connection for real-time frame-by-frame streaming analysis.

- **URL**: `ws://localhost:8000/api/v1/stream`
- **Protocol**: WebSocket

#### Frame Payload (Client ➔ Server):
Binary chunk of 16kHz PCM audio bytes.

#### Analysis Message (Server ➔ Client):
```json
{
  "chunk_index": 4,
  "instant_risk_score": 0.88,
  "status": "HIGH_RISK"
}
```
