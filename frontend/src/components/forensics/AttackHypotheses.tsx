import React from 'react';
import { Target, AlertCircle, Info, ShieldAlert, Cpu, Radio, Sparkles } from 'lucide-react';
import { AttackHypothesis } from '../../api/types';

interface AttackHypothesesProps {
  hypotheses: AttackHypothesis[];
}

export const AttackHypotheses: React.FC<AttackHypothesesProps> = ({ hypotheses }) => {
  const getLikelihoodBadge = (likelihood: AttackHypothesis['likelihood']) => {
    switch (likelihood) {
      case 'VERY_HIGH':
        return 'bg-rose-50 text-rose-800 border-rose-300';
      case 'HIGH':
        return 'bg-rose-50 text-rose-800 border-rose-200';
      case 'MODERATE':
        return 'bg-amber-50 text-amber-800 border-amber-300';
      default:
        return 'bg-[#F5F2EB] text-[#2F4156] border-[#C8D9E6]';
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-4">
      {/* Header with Scientific Disclaimer */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#C8D9E6]/60 pb-3">
        <div className="flex items-center space-x-2">
          <Target className="w-4 h-4 text-[#567C8D]" />
          <h3 className="font-bold text-[#2F4156] text-sm">
            Attack Vector Hypotheses ({hypotheses.length})
          </h3>
        </div>
        <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-[#F5F2EB] border border-[#C8D9E6] text-[10px] font-mono text-[#567C8D]">
          <Info className="w-3 h-3 text-[#567C8D] shrink-0" />
          <span>Qualitative Hypotheses &bull; Non-Definitive</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {hypotheses.map((hyp) => (
          <div
            key={hyp.id}
            className="p-4 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] space-y-2.5 flex flex-col justify-between"
          >
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-2">
                <h4 className="font-bold text-xs text-[#2F4156]">{hyp.name}</h4>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold border ${getLikelihoodBadge(hyp.likelihood)}`}>
                  {hyp.likelihood} LIKELIHOOD
                </span>
              </div>

              <p className="text-xs text-[#567C8D] leading-relaxed">
                {hyp.description}
              </p>
            </div>

            <div className="space-y-1.5 pt-2 border-t border-[#C8D9E6]/60">
              <span className="text-[10px] font-mono text-[#567C8D] font-semibold uppercase">
                Observed Indicators:
              </span>
              <ul className="space-y-1">
                {hyp.indicators.map((ind, idx) => (
                  <li key={idx} className="flex items-center space-x-1.5 text-[11px] text-[#2F4156]">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#567C8D] shrink-0" />
                    <span>{ind}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

