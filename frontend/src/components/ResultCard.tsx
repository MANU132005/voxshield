import React from 'react';
import { AnalysisResult } from '../types/analysis';
import { RiskGauge } from './RiskGauge';
import { ShieldCheck, ShieldAlert, AlertTriangle, Cpu, Radio, UserCheck, AlertCircle } from 'lucide-react';

interface ResultCardProps {
  result: AnalysisResult;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result }) => {
  const getStatusBadge = () => {
    switch (result.status) {
      case 'SAFE':
        return (
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 font-bold text-xs uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Status: SAFE</span>
          </div>
        );
      case 'SUSPICIOUS':
        return (
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-950/80 border border-amber-500/40 text-amber-400 font-bold text-xs uppercase tracking-wider">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Status: SUSPICIOUS</span>
          </div>
        );
      case 'HIGH_RISK':
        return (
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-950/80 border border-rose-500/40 text-rose-400 font-bold text-xs uppercase tracking-wider animate-pulse">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            <span>Status: HIGH RISK</span>
          </div>
        );
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
      
      {/* Top Header & Status */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h3 className="font-bold text-lg text-slate-100">Voice Impersonation Audit</h3>
          <p className="text-xs text-slate-400">Deepfake AI & Replay Security Evaluation</p>
        </div>
        {getStatusBadge()}
      </div>

      {/* Main Grid: Gauge + Detailed Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        
        {/* Left: Overall Risk Radial Gauge */}
        <div className="flex flex-col items-center justify-center p-4 bg-slate-900/60 rounded-xl border border-slate-800">
          <RiskGauge score={result.risk_score} status={result.status} />
          <span className="text-xs text-slate-400 mt-2 text-center font-medium">
            Aggregated Threat Score: <strong className="text-white">{result.risk_score}</strong>
          </span>
        </div>

        {/* Right: Metrics Progress Bars */}
        <div className="md:col-span-2 space-y-4">
          
          {/* Synthetic Score */}
          <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800/80 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center space-x-2 text-slate-300 font-medium">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>AI Synthetic Voice Score</span>
              </span>
              <span className="font-mono font-bold text-cyan-400">
                {(result.synthetic_score * 100).toFixed(1)}% ({result.synthetic_score})
              </span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-700"
                style={{ width: `${result.synthetic_score * 100}%` }}
              />
            </div>
          </div>

          {/* Replay Score */}
          <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800/80 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center space-x-2 text-slate-300 font-medium">
                <Radio className="w-4 h-4 text-amber-400" />
                <span>Acoustic Replay Score</span>
              </span>
              <span className="font-mono font-bold text-amber-400">
                {(result.replay_score * 100).toFixed(1)}% ({result.replay_score})
              </span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all duration-700"
                style={{ width: `${result.replay_score * 100}%` }}
              />
            </div>
          </div>

          {/* Speaker Match (Null Badge) */}
          <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800/80 flex items-center justify-between text-xs">
            <span className="flex items-center space-x-2 text-slate-400 font-medium">
              <UserCheck className="w-4 h-4 text-slate-500" />
              <span>Biometric Speaker Match</span>
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono text-[11px]">
              {result.speaker_match === null ? 'null (Phase 2)' : `${result.speaker_match}%`}
            </span>
          </div>

        </div>
      </div>

      {/* Diagnostic Reasons List */}
      <div className="pt-2">
        <h4 className="text-xs uppercase font-bold tracking-wider text-slate-400 mb-2.5 flex items-center space-x-1.5">
          <AlertCircle className="w-3.5 h-3.5 text-cyan-400" />
          <span>Diagnostic Findings ({result.reasons.length})</span>
        </h4>
        <div className="space-y-1.5">
          {result.reasons.map((reason, idx) => (
            <div
              key={idx}
              className="flex items-start space-x-2.5 p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-200"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
              <span>{reason}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
