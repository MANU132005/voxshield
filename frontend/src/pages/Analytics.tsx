import React from 'react';
import { Terminal, Code, Cpu, Layers, ArrowRight } from 'lucide-react';

export const Analytics: React.FC = () => {
  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">VoxShield API</h1>
        <p className="text-xs text-slate-400 mt-1">Developer integration and endpoint reference.</p>
      </div>

      {/* Architecture Flow Diagram */}
      <div className="bg-slate-900/80 rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>System Pipeline Architecture</span>
        </h3>

        <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 overflow-x-auto">
          <div className="flex items-center justify-between min-w-[700px] text-xs font-mono">
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center">Browser</div>
            <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center">Vercel Frontend</div>
            <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center">FastAPI Backend</div>
            <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center">Audio Preprocessor</div>
            <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center">PyTorch ResNet</div>
            <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center">Replay DSP</div>
            <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center">Risk Engine</div>
            <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-cyan-950 border border-cyan-500/40 text-cyan-300 text-center font-bold">Security Verdict</div>
          </div>
        </div>
      </div>

      {/* Grid Specs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Endpoint 1: Analyze */}
        <div className="bg-slate-900/60 rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 rounded-md bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-xs font-mono font-bold">
              POST
            </span>
            <code className="text-sm text-slate-200 font-mono font-semibold">/api/v1/analyze</code>
          </div>
          <p className="text-xs text-slate-300">Accepts multipart audio upload and returns synthetic probability, replay score, status, and diagnostic reasons.</p>
          
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-900 overflow-x-auto">
            <pre className="text-[11px] font-mono text-cyan-300 leading-relaxed">
{`{
  "synthetic_score": 0.01,
  "replay_score": 0.02,
  "risk_score": 0.01,
  "status": "SAFE",
  "verdict": "AUTHENTIC",
  "reasons": [
    "Acoustic features align with natural human voice"
  ]
}`}
            </pre>
          </div>
        </div>

        {/* Endpoint 2: Health & Readiness */}
        <div className="space-y-6">
          
          <div className="bg-slate-900/60 rounded-2xl p-6 border border-slate-800 space-y-3">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded-md bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
                GET
              </span>
              <code className="text-sm text-slate-200 font-mono font-semibold">/api/v1/health</code>
            </div>
            <p className="text-xs text-slate-300">Backend service status probe.</p>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-900">
              <pre className="text-[11px] font-mono text-emerald-300">
{`{ "status": "ok" }`}
              </pre>
            </div>
          </div>

          <div className="bg-slate-900/60 rounded-2xl p-6 border border-slate-800 space-y-3">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded-md bg-purple-950 text-purple-400 border border-purple-500/30 text-xs font-mono font-bold">
                GET
              </span>
              <code className="text-sm text-slate-200 font-mono font-semibold">/api/v1/ready</code>
            </div>
            <p className="text-xs text-slate-300">Readiness probe confirming PyTorch model checkpoint is loaded.</p>
          </div>

        </div>

      </div>

    </div>
  );
};
