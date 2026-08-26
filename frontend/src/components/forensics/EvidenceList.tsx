import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, Cpu, Radio, Activity, Sparkles, HelpCircle } from 'lucide-react';
import { ForensicEvidenceItem } from '../../api/types';

interface EvidenceListProps {
  evidenceList: ForensicEvidenceItem[];
}

export const EvidenceList: React.FC<EvidenceListProps> = ({ evidenceList }) => {
  if (evidenceList.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm text-center text-xs text-[#567C8D]">
        No active spoofing evidence indicators identified in the acoustic spectrum.
      </div>
    );
  }

  const getCategoryIcon = (category: ForensicEvidenceItem['category']) => {
    switch (category) {
      case 'SYNTHETIC_AI':
        return Cpu;
      case 'REPLAY_DSP':
        return Radio;
      default:
        return Activity;
    }
  };

  const getStrengthBadge = (strength: ForensicEvidenceItem['strength']) => {
    switch (strength) {
      case 'CRITICAL':
        return 'bg-rose-50 text-rose-800 border-rose-300';
      case 'HIGH':
        return 'bg-rose-50 text-rose-800 border-rose-200';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-800 border-amber-300';
      default:
        return 'bg-[#F5F2EB] text-[#2F4156] border-[#C8D9E6]';
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-[#C8D9E6]/60 pb-3">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-rose-600" />
          <h3 className="font-bold text-[#2F4156] text-sm">
            Primary Forensic Evidence ({evidenceList.length})
          </h3>
        </div>
        <span className="text-[11px] font-mono text-[#567C8D] font-medium">
          Acoustic Anomaly Vectors
        </span>
      </div>

      <div className="space-y-3">
        {evidenceList.map((item) => {
          const Icon = getCategoryIcon(item.category);
          const strengthStyle = getStrengthBadge(item.strength);

          return (
            <div
              key={item.id}
              className="p-4 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] space-y-2 hover:border-[#567C8D] transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center space-x-2.5">
                  <div className="p-1.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-600">
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-xs text-[#2F4156]">{item.title}</h4>
                    <span className="text-[10px] font-mono text-[#567C8D]">
                      Category: {item.category}
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold border ${strengthStyle}`}>
                    {item.strength}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-rose-50 border border-rose-200 text-rose-800 text-[10px] font-mono font-bold">
                    SUPPORTS SPOOF
                  </span>
                </div>
              </div>

              <p className="text-xs text-[#2F4156] leading-relaxed pl-8">
                {item.description}
              </p>

              {item.measuredValue !== undefined && (
                <div className="pl-8 pt-1 flex items-center space-x-2 text-[11px] font-mono text-[#567C8D]">
                  <span>Measured Value:</span>
                  <strong className="text-[#2F4156] font-bold">{item.measuredValue}</strong>
                  <span>&bull;</span>
                  <span>Status: {item.claimStatus}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

