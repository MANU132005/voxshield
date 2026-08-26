import React from 'react';
import { ShieldCheck, CheckCircle2, HeartHandshake, Info } from 'lucide-react';
import { ForensicEvidenceItem } from '../../api/types';

interface CounterEvidenceProps {
  counterEvidenceList: ForensicEvidenceItem[];
}

export const CounterEvidence: React.FC<CounterEvidenceProps> = ({ counterEvidenceList }) => {
  return (
    <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-[#C8D9E6]/60 pb-3">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-emerald-700" />
          <h3 className="font-bold text-[#2F4156] text-sm">
            Counter-Evidence & Genuine Traits ({counterEvidenceList.length})
          </h3>
        </div>
        <span className="text-[11px] font-mono text-[#567C8D] font-medium">
          Contradiction Analysis
        </span>
      </div>

      {counterEvidenceList.length === 0 ? (
        <div className="p-5 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] text-center space-y-1.5">
          <Info className="w-5 h-5 text-[#567C8D] mx-auto" />
          <p className="text-xs text-[#2F4156] font-medium">
            No counter-evidence observed in the acoustic spectrum.
          </p>
          <p className="text-[11px] text-[#567C8D] font-mono">
            Evaluated neural and DSP feature vectors decisively indicate anomalous spoof signatures.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {counterEvidenceList.map((item) => (
            <div
              key={item.id}
              className="p-4 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] space-y-2 hover:border-[#567C8D] transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center space-x-2.5">
                  <div className="p-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-xs text-[#2F4156]">{item.title}</h4>
                    <span className="text-[10px] font-mono text-[#567C8D]">
                      Category: {item.category}
                    </span>
                  </div>
                </div>

                <span className="px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-[10px] font-mono font-bold">
                  SUPPORTS GENUINE
                </span>
              </div>

              <p className="text-xs text-[#2F4156] leading-relaxed pl-8">
                {item.description}
              </p>

              {item.measuredValue !== undefined && (
                <div className="pl-8 pt-1 flex items-center space-x-2 text-[11px] font-mono text-[#567C8D]">
                  <span>Measured Baseline:</span>
                  <strong className="text-emerald-700 font-bold">{item.measuredValue}</strong>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

