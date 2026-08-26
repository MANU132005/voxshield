import React from 'react';
import { SearchCode, Shield, Mic2, ArrowLeft, Clock, FileAudio, Hash } from 'lucide-react';
import { EnrichedAnalysisResult } from '../api/types';
import { EvidenceList } from '../components/forensics/EvidenceList';
import { CounterEvidence } from '../components/forensics/CounterEvidence';
import { AttackHypotheses } from '../components/forensics/AttackHypotheses';
import { ConfidenceCard } from '../components/forensics/ConfidenceCard';
import { LimitationsCard } from '../components/forensics/LimitationsCard';
import { ForensicTimeline } from '../components/forensics/ForensicTimeline';
import { Badge } from '../components/common/Badge';
import { RequestIdCopy } from '../components/common/RequestIdCopy';
import { EmptyState } from '../components/common/EmptyState';
import { formatTime, formatFileSize } from '../utils/audioUtils';

interface ForensicInspectorProps {
  activeResult: EnrichedAnalysisResult | null;
  onNavigateToAnalyze: () => void;
}

export const ForensicInspector: React.FC<ForensicInspectorProps> = ({
  activeResult,
  onNavigateToAnalyze,
}) => {
  if (!activeResult) {
    return (
      <div className="space-y-8 pb-12 animate-in fade-in duration-300">
        <div className="border-b border-[#C8D9E6]/60 pb-5">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#2F4156] tracking-tight">
            Forensic Evidence & Explainability Inspector
          </h1>
          <p className="text-xs sm:text-sm text-[#567C8D] mt-0.5">
            Deep-dive acoustic signal intelligence, counter-evidence analysis, attack hypotheses, and execution timeline.
          </p>
        </div>

        <EmptyState
          title="No Active Voice Analysis In Context"
          description="Submit an audio recording or file upload in the Analyze Voice studio to populate full forensic telemetry, diagnostic reasons, and 10-stage processing timeline."
          icon={SearchCode}
          badgeText="AWAITING INFERENCE RESULT"
          actionButton={
            <button
              onClick={onNavigateToAnalyze}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-[#2F4156] hover:bg-[#19232f] text-white font-bold text-xs shadow-sm transition-all"
            >
              <Mic2 className="w-4 h-4" />
              <span>Go to Analyze Voice Studio</span>
            </button>
          }
        />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12 animate-in fade-in duration-300">
      
      {/* 1. Header with Active Audit Telemetry */}
      <div className="bg-white rounded-3xl p-6 border border-[#C8D9E6] shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] text-[10px] font-mono font-bold">
              ACTIVE AUDIT INSPECTION
            </span>
            <Badge variant={activeResult.decision} size="sm" />
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-[#2F4156] tracking-tight">
            Forensic Intelligence Report
          </h1>
          <div className="flex flex-wrap items-center gap-3 text-xs text-[#567C8D] font-mono">
            <span>Sample: <strong className="text-[#2F4156]">{activeResult.audioMetadata.name}</strong></span>
            <span>&bull;</span>
            <span>Latency: <strong className="text-[#2F4156]">{activeResult.latencyMs}ms</strong></span>
            <span>&bull;</span>
            <span>Threat Score: <strong className="text-[#2F4156]">{activeResult.raw.risk_score}</strong></span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-[#567C8D] font-mono text-[11px] font-medium">Audit ID:</span>
          <RequestIdCopy requestId={activeResult.requestId} />
        </div>
      </div>

      {/* 2. Top Grid: Confidence & Limitations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ConfidenceCard
          confidence={activeResult.confidence}
          explanation={activeResult.confidenceExplanation}
        />
        <LimitationsCard
          limitations={activeResult.limitations}
        />
      </div>

      {/* 3. Evidence & Counter-Evidence Pair */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EvidenceList
          evidenceList={activeResult.evidenceList}
        />
        <CounterEvidence
          counterEvidenceList={activeResult.counterEvidenceList}
        />
      </div>

      {/* 4. Attack Hypotheses */}
      <AttackHypotheses
        hypotheses={activeResult.attackHypotheses}
      />

      {/* 5. 10-Stage Processing Audit Timeline */}
      <ForensicTimeline
        timeline={activeResult.timeline}
        totalLatencyMs={activeResult.latencyMs}
      />

    </div>
  );
};

