import React from 'react';
import { Clock, CheckCircle2, Cpu, Radio, Shield, AudioWaveform, Layers, Activity, FileCheck2, Terminal } from 'lucide-react';
import { ForensicTimelineStage } from '../../api/types';

interface ForensicTimelineProps {
  timeline: ForensicTimelineStage[];
  totalLatencyMs: number;
}

export const ForensicTimeline: React.FC<ForensicTimelineProps> = ({
  timeline,
  totalLatencyMs,
}) => {
  return (
    <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#C8D9E6]/60 pb-4">
        <div className="flex items-center space-x-2.5">
          <Clock className="w-5 h-5 text-[#567C8D]" />
          <div>
            <h3 className="font-bold text-[#2F4156] text-sm sm:text-base">
              Forensic Processing Audit Trail
            </h3>
            <p className="text-xs text-[#567C8D]">10-Stage Pipeline Telemetry & Execution Lifecycle</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] text-xs font-mono">
          <span className="text-[#567C8D]">Total Roundtrip:</span>
          <strong className="text-[#2F4156] font-bold">{totalLatencyMs}ms</strong>
        </div>
      </div>

      {/* Timeline Steps List */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#C8D9E6]">
        {timeline.map((stage) => (
          <div key={stage.stageNumber} className="relative group">
            {/* Step marker dot */}
            <div className="absolute -left-[27px] top-1 w-5 h-5 rounded-full bg-white border-2 border-[#2F4156] flex items-center justify-center shadow-xs group-hover:scale-110 transition-transform">
              <span className="text-[9px] font-bold text-[#2F4156] font-mono">
                {stage.stageNumber}
              </span>
            </div>

            {/* Stage Card */}
            <div className="p-4 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] space-y-1.5 hover:border-[#567C8D] transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-bold text-xs text-[#2F4156]">{stage.name}</h4>
                  <span className="px-2 py-0.5 rounded bg-white border border-[#C8D9E6] text-[10px] font-mono text-[#2F4156] font-medium">
                    {stage.subsystem}
                  </span>
                </div>

                <div className="flex items-center space-x-2 text-[11px] font-mono text-[#567C8D]">
                  {stage.durationMs !== undefined && (
                    <span className="text-[#567C8D] font-medium">~{stage.durationMs}ms</span>
                  )}
                  <span className="px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-300 text-emerald-800 text-[9px] font-bold">
                    {stage.status}
                  </span>
                </div>
              </div>

              {stage.details && (
                <p className="text-xs text-[#2F4156] leading-relaxed font-sans">
                  {stage.details}
                </p>
              )}

              {stage.benchmarkNotes && (
                <p className="text-[10px] text-[#567C8D] font-mono font-medium">
                  Note: {stage.benchmarkNotes}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

