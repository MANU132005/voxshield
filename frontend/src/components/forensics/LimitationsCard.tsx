import React from 'react';
import { AlertCircle, Shield, Info, Lock } from 'lucide-react';

interface LimitationsCardProps {
  limitations: string[];
}

export const LimitationsCard: React.FC<LimitationsCardProps> = ({ limitations }) => {
  return (
    <div className="bg-white rounded-2xl p-5 border border-[#C8D9E6] shadow-sm space-y-3">
      <div className="flex items-center space-x-2">
        <AlertCircle className="w-4 h-4 text-[#567C8D]" />
        <h4 className="text-xs font-bold text-[#2F4156]">
          Scientific Boundaries & Limitations
        </h4>
      </div>

      <ul className="space-y-2">
        {limitations.map((lim, idx) => (
          <li key={idx} className="flex items-start space-x-2 text-xs text-[#567C8D] leading-relaxed">
            <span className="w-1.5 h-1.5 rounded-full bg-[#567C8D] mt-1.5 shrink-0" />
            <span>{lim}</span>
          </li>
        ))}
      </ul>

      <div className="pt-2 border-t border-[#C8D9E6]/60 flex items-center space-x-2 text-[10px] font-mono text-[#567C8D]">
        <Lock className="w-3 h-3 text-[#567C8D]" />
        <span>VoxShield Certified Scientific Integrity Framework</span>
      </div>
    </div>
  );
};

