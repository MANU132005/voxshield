import React from 'react';
import { Gauge, CheckCircle2, AlertTriangle, AlertOctagon, HelpCircle, ShieldCheck } from 'lucide-react';
import { ConfidenceState } from '../../api/types';

interface ConfidenceCardProps {
  confidence: ConfidenceState;
  explanation: string;
}

export const ConfidenceCard: React.FC<ConfidenceCardProps> = ({
  confidence,
  explanation,
}) => {
  const getConfig = () => {
    switch (confidence) {
      case 'HIGH_MEASUREMENT_CONFIDENCE':
        return {
          label: 'HIGH MEASUREMENT CONFIDENCE',
          icon: ShieldCheck,
          textColor: 'text-emerald-700',
          borderColor: 'border-emerald-300',
          bgBadge: 'bg-emerald-50 text-emerald-800 border-emerald-300',
          description: 'Acoustic parameters and model activation boundaries show strong, clear separation.',
        };
      case 'MODERATE':
        return {
          label: 'MODERATE CONFIDENCE',
          icon: AlertTriangle,
          textColor: 'text-amber-700',
          borderColor: 'border-amber-300',
          bgBadge: 'bg-amber-50 text-amber-800 border-amber-300',
          description: 'Signal measurements reside in the transitional decision corridor.',
        };
      case 'LOW':
        return {
          label: 'LOW CONFIDENCE',
          icon: AlertOctagon,
          textColor: 'text-rose-700',
          borderColor: 'border-rose-300',
          bgBadge: 'bg-rose-50 text-rose-800 border-rose-300',
          description: 'Conflicting or noisy acoustic cues limit definitive measurement resolution.',
        };
      default:
        return {
          label: 'INSUFFICIENT EVIDENCE',
          icon: HelpCircle,
          textColor: 'text-[#567C8D]',
          borderColor: 'border-[#C8D9E6]',
          bgBadge: 'bg-[#F5F2EB] text-[#2F4156] border-[#C8D9E6]',
          description: 'Signal length or SNR is insufficient for statistical confidence.',
        };
    }
  };

  const config = getConfig();
  const Icon = config.icon;

  return (
    <div className={`bg-white rounded-2xl p-5 border ${config.borderColor} shadow-sm space-y-3`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Icon className={`w-4 h-4 ${config.textColor}`} />
          <span className="text-xs font-bold text-[#2F4156]">Measurement Confidence</span>
        </div>
        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${config.bgBadge}`}>
          {confidence}
        </span>
      </div>

      <p className="text-xs text-[#567C8D] leading-relaxed">
        {explanation || config.description}
      </p>

      <div className="pt-2 border-t border-[#C8D9E6]/60 flex items-center justify-between text-[10px] font-mono text-[#567C8D]">
        <span>ClaimGuard Evaluation</span>
        <span>Acoustic Separation Index</span>
      </div>
    </div>
  );
};

