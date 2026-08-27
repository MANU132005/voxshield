import React, { useState } from 'react';
import { AnalysisResult } from '../types/analysis';
import { RiskGauge } from './RiskGauge';
import { ShieldCheck, ShieldAlert, AlertTriangle, Cpu, Radio, AlertCircle, ChevronDown, ChevronUp, RefreshCw, FileText, CheckCircle2 } from 'lucide-react';

interface ResultCardProps {
  result: AnalysisResult;
  onReset?: () => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result, onReset }) => {
  const [showTechnical, setShowTechnical] = useState<boolean>(false);

  const getVerdictBadge = () => {
    switch (result.status) {
      case 'SAFE':
        return (
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-emerald-950 border border-emerald-500/50 text-emerald-400 font-extrabold text-sm uppercase tracking-widest">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>SAFE</span>
          </div>
        );
      case 'SUSPICIOUS':
        return (
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-amber-950 border border-amber-500/50 text-amber-400 font-extrabold text-sm uppercase tracking-widest">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>SUSPICIOUS</span>
          </div>
        );
      case 'HIGH_RISK':
        return (
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-rose-950 border border-rose-500/50 text-rose-400 font-extrabold text-sm uppercase tracking-widest">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <span>HIGH RISK</span>
          </div>
        );
    }
  };

  return (
    <div className="bg-slate-900/80 rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
      
      {/* Mode Banner */}
      {result.isDemo && (
        <div className="p-3 rounded-xl bg-amber-950/80 border border-amber-500/40 text-amber-300 text-xs font-semibold flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>DEMO SIMULATION — Offline demonstration sample (Not a live security analysis)</span>
          </div>
        </div>
      )}

      {/* Security Verdict Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-5 gap-4">
        <div>
          <span className="text-[11px] uppercase tracking-wider font-bold text-slate-400">Security Verdict</span>
          <h3 className="font-extrabold text-xl text-white mt-0.5">Voice Authenticity Evaluation</h3>
        </div>
        <div>
          {getVerdictBadge()}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        
        {/* Metric 1: Risk Gauge */}
        <div className="flex flex-col items-center justify-center p-5 bg-slate-950/60 rounded-xl border border-slate-800/80">
          <RiskGauge score={result.risk_score} status={result.status} />
          <div className="mt-3 text-center">
            <span className="text-xs text-slate-400 uppercase tracking-wider font-bold block">Overall Risk</span>
            <span className="text-lg font-mono font-bold text-white">{result.risk_score}</span>
          </div>
        </div>

        {/* Metric 2 & 3 Cards */}
        <div className="md:col-span-2 space-y-4">
          
          {/* AI Synthetic Voice */}
          <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center space-x-2 text-slate-300 font-semibold">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>AI SYNTHETIC VOICE</span>
              </span>
              <span className="font-mono font-bold text-cyan-400 text-sm">
                {(result.synthetic_score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-500 transition-all duration-700"
                style={{ width: `${result.synthetic_score * 100}%` }}
              />
            </div>
          </div>

          {/* Acoustic Replay */}
          <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center space-x-2 text-slate-300 font-semibold">
                <Radio className="w-4 h-4 text-amber-400" />
                <span>ACOUSTIC REPLAY</span>
              </span>
              <span className="font-mono font-bold text-amber-400 text-sm">
                {(result.replay_score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 transition-all duration-700"
                style={{ width: `${result.replay_score * 100}%` }}
              />
            </div>
          </div>

        </div>
      </div>

      {/* Explainability: Why this verdict? */}
      <div className="p-5 bg-slate-950/80 rounded-xl border border-slate-800 space-y-3">
        <h4 className="text-xs uppercase font-bold tracking-wider text-slate-300 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-cyan-400" />
          <span>Why this verdict?</span>
        </h4>
        <div className="space-y-2">
          {result.reasons.map((reason, idx) => (
            <div key={idx} className="flex items-start space-x-2.5 text-xs text-slate-200">
              {result.status === 'SAFE' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              )}
              <span>{reason}</span>
            </div>
          ))}
        </div>

        {/* Structured Evidence (if returned) */}
        {result.evidence && result.evidence.length > 0 && (
          <div className="pt-3 border-t border-slate-900 space-y-2">
            <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider block">Observed Neural & Acoustic Evidence</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {result.evidence.map((item, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] space-y-1">
                  <div className="flex items-center justify-between text-slate-300 font-semibold">
                    <span>{item.code || item.category}</span>
                    <span className="font-mono text-cyan-400">{item.observed_value ? (item.observed_value * 100).toFixed(1) + '%' : ''}</span>
                  </div>
                  <p className="text-slate-400">{item.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Collapsible Technical Forensic Analysis */}
      <div className="pt-2">
        <button
          onClick={() => setShowTechnical(!showTechnical)}
          className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 transition-all"
        >
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <span>Technical Analysis</span>
          </div>
          {showTechnical ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </button>

        {showTechnical && (
          <div className="mt-3 p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-4 font-mono">
            <div>
              <span className="text-slate-400 uppercase tracking-wider text-[10px] block mb-1">Scientific Decision</span>
              <p className="text-cyan-300 font-semibold">{result.verdict} (Risk Level: {result.risk_level || 'N/A'})</p>
            </div>

            {result.forensic_timeline && result.forensic_timeline.length > 0 && (
              <div>
                <span className="text-slate-400 uppercase tracking-wider text-[10px] block mb-2">Forensic Execution Timeline</span>
                <div className="space-y-1 text-[11px]">
                  {result.forensic_timeline.map((stage, idx) => (
                    <div key={idx} className="flex items-center justify-between py-1 border-b border-slate-900 text-slate-300">
                      <span>{stage.stage_id}. {stage.stage_name}</span>
                      <span className="text-slate-400">{stage.execution_time_ms.toFixed(2)} ms</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="text-[10px] text-slate-500">
              Evaluator Version: {result.evaluator_version || 'risk_engine_v1.0'} | ResNet Architecture: 2D CNN (80 Log-Mel + 20 LFCC)
            </div>
          </div>
        )}
      </div>

      {/* Result Actions */}
      <div className="pt-2 flex items-center justify-between border-t border-slate-800">
        {onReset && (
          <button
            onClick={onReset}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Analyze Another Sample</span>
          </button>
        )}
      </div>

    </div>
  );
};
