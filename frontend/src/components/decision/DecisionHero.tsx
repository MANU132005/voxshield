import React from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Info,
  Clock,
  FileAudio,
  Hash,
  Activity,
  Layers,
  Sparkles,
} from 'lucide-react';
import { EnrichedAnalysisResult } from '../../api/types';
import { RiskIndexGauge } from './RiskIndexGauge';
import { Badge } from '../common/Badge';
import { RequestIdCopy } from '../common/RequestIdCopy';
import { formatTime, formatFileSize } from '../../utils/audioUtils';

interface DecisionHeroProps {
  enrichedResult: EnrichedAnalysisResult;
}

export const DecisionHero: React.FC<DecisionHeroProps> = ({ enrichedResult }) => {
  const { decision, decisionReason, raw, confidence, confidenceExplanation, audioMetadata, latencyMs, requestId } =
    enrichedResult;

  const getDecisionHeader = () => {
    switch (decision) {
      case 'ALLOW':
        return {
          title: 'AUTHENTICATION PERMITTED',
          subtitle: 'Voice sample verified as genuine biological human speech.',
          borderColor: 'border-emerald-300',
          decisionIcon: ShieldCheck,
          accentText: 'text-emerald-700',
        };
      case 'STEP-UP':
        return {
          title: 'STEP-UP VERIFICATION REQUIRED',
          subtitle: 'Acoustic anomalies detected. Secondary out-of-band verification recommended.',
          borderColor: 'border-amber-300',
          decisionIcon: AlertTriangle,
          accentText: 'text-amber-700',
        };
      case 'BLOCK':
        return {
          title: 'VOICE SPOOF BLOCKED',
          subtitle: 'High-risk synthetic AI voice clone or physical audio replay detected.',
          borderColor: 'border-rose-300',
          decisionIcon: ShieldAlert,
          accentText: 'text-rose-700',
        };
      default:
        return {
          title: 'ANALYSIS INCONCLUSIVE',
          subtitle: 'Insufficient acoustic signal definition to formulate a definitive security decision.',
          borderColor: 'border-[#C8D9E6]',
          decisionIcon: Info,
          accentText: 'text-[#567C8D]',
        };
    }
  };

  const config = getDecisionHeader();
  const DecisionIcon = config.decisionIcon;

  return (
    <div
      className={`bg-white rounded-3xl p-6 sm:p-8 border ${config.borderColor} space-y-6 shadow-sm relative overflow-hidden`}
    >
      
      {/* Top Banner: Decision Badge + Request Audit ID */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#C8D9E6]/60 pb-5">
        <div className="flex items-center space-x-3">
          <Badge variant={decision} size="lg" />
          <Badge variant={raw.status} size="md" />
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-[#567C8D] font-mono text-[11px] font-medium">Audit ID:</span>
          <RequestIdCopy requestId={requestId} />
        </div>
      </div>

      {/* Main HERO Grid: Giant Decision Statement + Radial Risk Gauge */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">
        
        {/* Left 2 Cols: Main Decision Headline & Reasoning */}
        <div className="lg:col-span-2 space-y-4">
          <div className="space-y-2">
            <div className="flex items-center space-x-2.5">
              <DecisionIcon className={`w-7 h-7 ${config.accentText} shrink-0`} />
              <h2 className="text-2xl sm:text-3xl font-black text-[#2F4156] tracking-tight">
                {config.title}
              </h2>
            </div>
            <p className="text-sm text-[#567C8D] font-medium leading-relaxed">
              {config.subtitle}
            </p>
          </div>

          {/* Detailed Decision Rationale Box */}
          <div className="p-4 rounded-2xl bg-[#F5F2EB] border border-[#C8D9E6] space-y-2">
            <div className="flex items-center space-x-2 text-xs font-bold text-[#2F4156]">
              <Sparkles className="w-3.5 h-3.5 text-[#567C8D]" />
              <span>Policy Enforcement Rationale</span>
            </div>
            <p className="text-xs text-[#567C8D] leading-relaxed font-normal">
              {decisionReason}
            </p>
          </div>

          {/* Telemetry Tags */}
          <div className="flex flex-wrap items-center gap-3 text-xs pt-1">
            <div className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] font-mono">
              <Clock className="w-3.5 h-3.5 text-[#567C8D]" />
              <span>Inference Latency: <strong>{latencyMs}ms</strong></span>
            </div>

            <div className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] font-mono">
              <FileAudio className="w-3.5 h-3.5 text-[#567C8D]" />
              <span className="truncate max-w-[160px] font-semibold">{audioMetadata.name}</span>
              {audioMetadata.durationSeconds ? (
                <span className="text-[#567C8D]">({formatTime(audioMetadata.durationSeconds)})</span>
              ) : null}
            </div>

            <div className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] font-mono">
              <Activity className="w-3.5 h-3.5 text-[#567C8D]" />
              <span>Confidence: <strong className="text-[#2F4156]">{confidence}</strong></span>
            </div>
          </div>
        </div>

        {/* Right Col: High Precision Circular Gauge */}
        <div className="flex flex-col items-center justify-center p-6 bg-[#F5F2EB] rounded-2xl border border-[#C8D9E6] shadow-xs">
          <RiskIndexGauge score={raw.risk_score} status={raw.status} size={150} />
          <div className="mt-3 text-center space-y-0.5">
            <p className="text-xs font-bold text-[#2F4156]">Aggregated Threat Score</p>
            <p className="text-[10px] font-mono text-[#567C8D] font-medium">
              Formula: 0.6 &times; P(synth) + 0.4 &times; P(replay)
            </p>
          </div>
        </div>

      </div>

    </div>
  );
};

