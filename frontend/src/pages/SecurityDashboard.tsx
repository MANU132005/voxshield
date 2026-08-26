import React from 'react';
import { Shield, Activity, Mic2, AlertTriangle, ShieldAlert, ShieldCheck, Clock, FileAudio, ArrowRight, Layers, Sparkles } from 'lucide-react';
import { HealthCheckResult } from '../api/healthApi';
import { SessionAuditRecord, EnrichedAnalysisResult } from '../api/types';
import { HealthBanner } from '../components/dashboard/HealthBanner';
import { SessionAuditTable } from '../components/dashboard/SessionAuditTable';
import { RoadmapMatrix } from '../components/dashboard/RoadmapMatrix';
import { MetricCard } from '../components/common/MetricCard';

interface SecurityDashboardProps {
  health: HealthCheckResult | null;
  isCheckingHealth: boolean;
  onRefreshHealth: () => void;
  sessionRecords: SessionAuditRecord[];
  onSelectRecord: (record: SessionAuditRecord) => void;
  onNavigateToAnalyze: () => void;
  onClearSession: () => void;
}

export const SecurityDashboard: React.FC<SecurityDashboardProps> = ({
  health,
  isCheckingHealth,
  onRefreshHealth,
  sessionRecords,
  onSelectRecord,
  onNavigateToAnalyze,
  onClearSession,
}) => {
  const totalAudits = sessionRecords.length;
  const blockedThreats = sessionRecords.filter((r) => r.decision === 'BLOCK').length;
  const allowedSafe = sessionRecords.filter((r) => r.decision === 'ALLOW').length;
  const stepUpVerifications = sessionRecords.filter((r) => r.decision === 'STEP-UP').length;

  const avgLatency = totalAudits > 0
    ? Math.round(sessionRecords.reduce((acc, r) => acc + r.latencyMs, 0) / totalAudits)
    : (health?.latencyMs || 0);

  return (
    <div className="space-y-8 pb-12 animate-in fade-in duration-300">
      
      {/* 1. Hero Welcome & Launch Banner */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#C8D9E6] shadow-sm relative overflow-hidden">
        <div className="max-w-3xl space-y-3 relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] text-xs font-semibold font-mono">
            <Shield className="w-3.5 h-3.5 text-[#567C8D]" />
            <span>SIH26104 &bull; VOICE SECURITY PLATFORM</span>
          </div>

          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-[#2F4156] tracking-tight">
            AI Voice Impersonation & Deepfake Security Console
          </h1>

          <p className="text-xs sm:text-sm text-[#567C8D] leading-relaxed max-w-2xl">
            VoxShield provides multi-stage voice anti-spoofing defense combining deep learning neural classifiers, digital signal processing (DSP) acoustic reverberation analysis, and contextual risk evaluation.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={onNavigateToAnalyze}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-[#2F4156] hover:bg-[#19232f] text-white font-bold text-xs sm:text-sm shadow-sm transition-all"
            >
              <Mic2 className="w-4 h-4" />
              <span>Launch Voice Analysis Studio</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* 2. Live Health & Operational Status Banner */}
      <HealthBanner
        health={health}
        isChecking={isCheckingHealth}
        onRefresh={onRefreshHealth}
      />

      {/* 3. High-Priority SOC Telemetry Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Gateway Status"
          value={health?.isOnline ? 'ONLINE' : 'OFFLINE'}
          subtitle="FastAPI REST API"
          icon={Activity}
          accentColor={health?.isOnline ? 'emerald' : 'rose'}
          badge={health?.isOnline ? 'HTTP 200' : 'UNREACHABLE'}
        />

        <MetricCard
          title="Session Audits"
          value={totalAudits}
          subtitle="In-memory session count"
          icon={FileAudio}
          accentColor="cyan"
          trend={totalAudits > 0 ? `${allowedSafe} Safe / ${blockedThreats} Blocked` : 'Awaiting input'}
        />

        <MetricCard
          title="Threat Blocks"
          value={blockedThreats}
          subtitle="High-risk spoof attempts"
          icon={ShieldAlert}
          accentColor="rose"
          badge={totalAudits > 0 ? `${Math.round((blockedThreats / totalAudits) * 100)}% Flagged` : '0%'}
        />

        <MetricCard
          title="Avg Inference Latency"
          value={`${avgLatency}ms`}
          subtitle="Roundtrip pipeline time"
          icon={Clock}
          accentColor="purple"
          trend="Sub-second response"
        />
      </div>

      {/* 4. Session Investigation Log Table */}
      <SessionAuditTable
        records={sessionRecords}
        onSelectRecord={onSelectRecord}
        onClearSession={onClearSession}
      />

      {/* 5. Phased Roadmap & Capabilities Matrix */}
      <RoadmapMatrix />

    </div>
  );
};

