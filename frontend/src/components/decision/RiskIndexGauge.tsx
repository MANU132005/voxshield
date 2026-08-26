import React from 'react';
import { BackendRiskStatus } from '../../api/types';

interface RiskIndexGaugeProps {
  score: number; // 0.0 - 1.0
  status: BackendRiskStatus;
  size?: number;
}

export const RiskIndexGauge: React.FC<RiskIndexGaugeProps> = ({
  score,
  status,
  size = 140,
}) => {
  const percentage = Math.round(score * 100);

  const getTheme = () => {
    switch (status) {
      case 'SAFE':
        return {
          stroke: '#15803d', // emerald-700
          glow: 'none',
          textColor: 'text-emerald-700',
          label: 'LOW THREAT',
        };
      case 'SUSPICIOUS':
        return {
          stroke: '#b45309', // amber-700
          glow: 'none',
          textColor: 'text-amber-700',
          label: 'ELEVATED RISK',
        };
      case 'HIGH_RISK':
        return {
          stroke: '#b91c1c', // rose-700
          glow: 'none',
          textColor: 'text-rose-700',
          label: 'CRITICAL RISK',
        };
    }
  };

  const theme = getTheme();
  const strokeWidth = 10;
  const radius = (size - strokeWidth * 2) / 2;
  const center = size / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - score * circumference;

  return (
    <div className="flex flex-col items-center justify-center relative select-none">
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background full track in Sky Blue */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          className="stroke-[#C8D9E6]"
          strokeWidth={strokeWidth}
          fill="transparent"
        />

        {/* Dynamic risk score arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          stroke={theme.stroke}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          fill="transparent"
          className="transition-all duration-1000 ease-out"
        />
      </svg>

      {/* Center typography */}
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-3xl sm:text-4xl font-black text-[#2F4156] tracking-tight font-mono">
          {percentage}
        </span>
        <span className={`text-[10px] uppercase font-mono font-bold tracking-widest ${theme.textColor}`}>
          {theme.label}
        </span>
        <span className="text-[9px] font-mono text-[#567C8D] mt-0.5 font-medium">
          RAW {score.toFixed(2)}
        </span>
      </div>
    </div>
  );
};

