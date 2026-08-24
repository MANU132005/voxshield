import React from 'react';
import { Terminal, Code, Cpu, Layers } from 'lucide-react';

export const Analytics: React.FC = () => {
  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">API Contract & Architecture Specs</h1>
        <p className="text-xs text-slate-400 mt-1">Detailed RESTful & WebSocket API specifications for Developer 1 & 2</p>
      </div>

      {/* Grid Specs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Endpoint 1: Analyze */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 rounded-md bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-xs font-mono font-bold">
              POST
            </span>
            <code className="text-sm text-slate-200 font-mono font-semibold">/api/v1/analyze</code>
          </div>
          <p className="text-xs text-slate-300">Accepts audio file upload and returns synthetic probability, replay score, status, and diagnostic reasons.</p>
          
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-900 overflow-x-auto">
            <pre className="text-[11px] font-mono text-cyan-300 leading-relaxed">
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

        {/* Endpoint 2: Health Check & WebSocket */}
        <div className="space-y-6">
          
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-3">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded-md bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
                GET
              </span>
              <code className="text-sm text-slate-200 font-mono font-semibold">/api/v1/health</code>
            </div>
            <p className="text-xs text-slate-300">Backend health status check.</p>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-900">
              <pre className="text-[11px] font-mono text-emerald-300">
{`{ "status": "ok" }`}
              </pre>
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-3">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded-md bg-purple-950 text-purple-400 border border-purple-500/30 text-xs font-mono font-bold">
                WS
              </span>
              <code className="text-sm text-slate-200 font-mono font-semibold">/api/v1/stream</code>
            </div>
            <p className="text-xs text-slate-300">WebSocket connection endpoint structure prepared for future real-time streaming analysis.</p>
          </div>

        </div>

      </div>

      {/* Developer Scoping Table */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="font-bold text-base text-slate-100 flex items-center space-x-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>Team Responsibility Isolation</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <h4 className="font-bold text-cyan-400 text-sm">Developer 1 (Backend & AI)</h4>
            <ul className="space-y-1 text-slate-300 list-disc list-inside">
              <li>Primary Folder: <code className="text-cyan-300">backend/</code></li>
              <li>FastAPI Endpoints & Pydantic Validation</li>
              <li>PyTorch Anti-Spoofing Model Weights & Inference</li>
              <li>LFCC/MFCC Spectrogram Feature Extraction</li>
              <li>DSP Room Reverberation & Risk Engine</li>
            </ul>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <h4 className="font-bold text-emerald-400 text-sm">Developer 2 (Frontend & UX)</h4>
            <ul className="space-y-1 text-slate-300 list-disc list-inside">
              <li>Primary Folder: <code className="text-emerald-300">frontend/</code></li>
              <li>React + Tailwind CSS Dashboard Components</li>
              <li>Microphone Web Audio API Recording</li>
              <li>Waveform Visualizers & Risk Radial Meters</li>
              <li>Mock Service Layer & Axios Client Integration</li>
            </ul>
          </div>

        </div>
      </div>

    </div>
  );
};
