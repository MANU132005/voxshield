import React from 'react';
import { Terminal, FileCode2, Layers, Cpu, Radio, Shield, Network, ArrowUpRight, Copy, Check } from 'lucide-react';
import { API_V1_URL } from '../api/client';

export const SystemArchitecture: React.FC = () => {
  const [copiedEndpoint, setCopiedEndpoint] = React.useState<string | null>(null);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedEndpoint(id);
    setTimeout(() => setCopiedEndpoint(null), 2000);
  };

  return (
    <div className="space-y-8 pb-12 animate-in fade-in duration-300">
      
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#C8D9E6]/60 pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] text-[10px] font-mono font-bold">
              SYSTEM & API SPECIFICATIONS
            </span>
            <span className="text-[11px] text-[#567C8D] font-mono font-medium">v1.0.0</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#2F4156] tracking-tight mt-1">
            API Contract & Security Architecture
          </h1>
          <p className="text-xs sm:text-sm text-[#567C8D] mt-0.5">
            Technical RESTful and WebSocket API specifications interfacing the FastAPI backend and React SOC client.
          </p>
        </div>

        <a
          href={`${API_V1_URL}/docs`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-[#567C8D] hover:bg-[#476878] text-white border border-[#2F4156] text-xs font-mono font-bold transition-all shrink-0 shadow-xs"
        >
          <span>Open Interactive Swagger</span>
          <ArrowUpRight className="w-4 h-4" />
        </a>
      </div>

      {/* 2. Discovered Endpoints Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Endpoint 1: POST /api/v1/analyze */}
        <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="px-2.5 py-1 rounded-lg bg-[#2F4156] text-white text-xs font-mono font-bold">
                POST
              </span>
              <code className="text-xs sm:text-sm text-[#2F4156] font-mono font-bold">
                /api/v1/analyze
              </code>
            </div>
            <button
              onClick={() => handleCopy('POST /api/v1/analyze', 'analyze')}
              className="p-1.5 rounded-lg bg-[#F5F2EB] border border-[#C8D9E6] text-[#567C8D] hover:text-[#2F4156] transition-colors"
              title="Copy endpoint"
            >
              {copiedEndpoint === 'analyze' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>

          <p className="text-xs text-[#567C8D] leading-relaxed">
            Primary multi-stage audio inference endpoint. Accepts binary audio stream (<code className="text-[#2F4156] font-bold font-mono">multipart/form-data</code>) and returns synthetic probability, replay DSP score, threat status, and diagnostic reasons.
          </p>

          <div className="space-y-2">
            <span className="text-[10px] font-mono text-[#567C8D] uppercase font-bold tracking-wider">
              Response Contract (200 OK):
            </span>
            <div className="p-3.5 bg-[#F5F2EB] rounded-xl border border-[#C8D9E6] overflow-x-auto">
              <pre className="text-[11px] font-mono text-[#2F4156] leading-relaxed font-semibold">
{`{
  "synthetic_score": 0.91,
  "replay_score": 0.73,
  "speaker_match": null,
  "risk_score": 0.89,
  "status": "HIGH_RISK",
  "reasons": [
    "Synthetic voice characteristics detected",
    "Possible replay characteristics detected"
  ]
}`}
              </pre>
            </div>
          </div>
        </div>

        {/* Endpoint 2 & 3: Health and WebSocket Stream */}
        <div className="space-y-6">
          
          {/* GET /api/v1/health */}
          <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-300 text-xs font-mono font-bold">
                  GET
                </span>
                <code className="text-xs sm:text-sm text-[#2F4156] font-mono font-bold">
                  /api/v1/health
                </code>
              </div>
              <button
                onClick={() => handleCopy('GET /api/v1/health', 'health')}
                className="p-1.5 rounded-lg bg-[#F5F2EB] border border-[#C8D9E6] text-[#567C8D] hover:text-[#2F4156] transition-colors"
                title="Copy endpoint"
              >
                {copiedEndpoint === 'health' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>

            <p className="text-xs text-[#567C8D]">
              Health check service verifying FastAPI application and anti-spoofing gateway readiness.
            </p>

            <div className="p-3.5 bg-[#F5F2EB] rounded-xl border border-[#C8D9E6]">
              <pre className="text-[11px] font-mono text-emerald-700 font-bold">
{`{ "status": "ok" }`}
              </pre>
            </div>
          </div>

          {/* WS /api/v1/stream (Phase 2) */}
          <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <span className="px-2.5 py-1 rounded-lg bg-[#C8D9E6]/50 text-[#2F4156] border border-[#C8D9E6] text-xs font-mono font-bold">
                  WS
                </span>
                <code className="text-xs sm:text-sm text-[#2F4156] font-mono font-bold">
                  /api/v1/stream
                </code>
              </div>
              <span className="px-2 py-0.5 rounded bg-[#C8D9E6]/60 text-[#2F4156] border border-[#C8D9E6] text-[9px] font-mono font-bold">
                PHASE 2 ROADMAP
              </span>
            </div>

            <p className="text-xs text-[#567C8D] leading-relaxed">
              WebSocket streaming protocol for real-time frame-by-frame PCM audio chunk analysis and instant rolling risk evaluation.
            </p>
          </div>

        </div>

      </div>

      {/* 3. System Architecture Diagram */}
      <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-4">
        <div className="flex items-center space-x-2 text-[#2F4156] font-bold text-base">
          <Network className="w-5 h-5 text-[#567C8D]" />
          <h3>High-Level Data Pipeline & Component Architecture</h3>
        </div>

        <div className="p-4 bg-[#F5F2EB] rounded-2xl border border-[#C8D9E6] overflow-x-auto">
          <pre className="text-[11px] font-mono text-[#2F4156] leading-relaxed font-medium">
{`Microphone / Audio File Upload (WAV, MP3, FLAC, M4A, OGG)
             │
             ▼
    React 18 + Vite SOC Console (Web Audio Spectrum & AudioUploader)
             │
             ▼ POST /api/v1/analyze (multipart/form-data)
    FastAPI Security Gateway
             │
    ┌────────┴────────────────────────┬────────────────────────┐
    │                                 │                        │
    ▼                                 ▼                        ▼
Acoustic Normalizer           Deep Neural Classifier    Replay DSP Analyzer
(16kHz mono PCM)              (LFCC / Spectrogram CNN)  (Room Impulse Reverberation)
    │                                 │                        │
    └─────────────────┬───────────────┘                        │
                      │ P(synthetic)                           │ P(replay)
                      ▼                                        ▼
             ┌──────────────────────────────────────────────────┐
             │ CONTEXTUAL RISK ENGINE (Heuristic & Weighting)   │
             │ Formula: 0.6 × P(synth) + 0.4 × P(replay)        │
             └────────────────────────┬─────────────────────────┘
                                      │
                                      ▼
             JSON Security Audit Report ➔ React SOC Console`}
          </pre>
        </div>
      </div>

    </div>
  );
};

