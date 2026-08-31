import React from 'react';
import { Terminal, Code, Cpu, Layers, ArrowRight, ExternalLink, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const Analytics: React.FC = () => {
  const backendBaseUrl = 'https://voxshield-backend-wg3p.onrender.com';

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800">
        <div>
          <span className="text-[11px] uppercase tracking-widest font-extrabold text-cyan-400">VOXSHIELD API</span>
          <h1 className="text-xl sm:text-2xl font-bold text-white mt-1">Developer Integration & Architecture</h1>
          <p className="text-xs text-slate-400 mt-1">Production REST API endpoints and system architecture for integrating VoxShield audio anti-spoofing.</p>
        </div>

        <a
          href={`${backendBaseUrl}/api/v1/docs`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md transition-all shrink-0"
        >
          <span>Open Interactive Swagger Docs</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* Architecture Flow Diagram */}
      <div className="bg-slate-900/80 rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest flex items-center space-x-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>SYSTEM PIPELINE ARCHITECTURE</span>
        </h3>

        <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 overflow-x-auto">
          <div className="flex items-center justify-between min-w-[850px] text-[11px] font-mono">
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center font-bold">USER</div>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center font-bold">VOXSHIELD WEB APP</div>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center font-bold">FASTAPI</div>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center font-bold">AUDIO PROCESSING</div>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center font-bold">FEATURE EXTRACTION</div>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center font-bold">PYTORCH ANTI-SPOOFING + REPLAY DSP</div>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-center font-bold">RISK ENGINE</div>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <div className="px-3 py-2 rounded-lg bg-cyan-950 border border-cyan-500/50 text-cyan-300 text-center font-bold">SECURITY VERDICT</div>
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
