import React from 'react';
import { RiskStatus } from '../types/analysis';

interface RiskGaugeProps {
  score: number;
  status: RiskStatus;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score, status }) => {
  const percentage = Math.round(score * 100);

  const getStatusColor = () => {
    switch (status) {
      case 'SAFE':
        return {
          stroke: '#10b981',
          bg: 'bg-emerald-500/10',
          text: 'text-emerald-400',
          border: 'border-emerald-500/30'
        };
      case 'SUSPICIOUS':
        return {
          stroke: '#f59e0b',
          bg: 'bg-amber-500/10',
          text: 'text-amber-400',
          border: 'border-amber-500/30'
        };
      case 'HIGH_RISK':
        return {
          stroke: '#ef4444',
          bg: 'bg-rose-500/10',
          text: 'text-rose-400',
          border: 'border-rose-500/30'
        };
    }
  };

  const style = getStatusColor();
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score * circumference);

  return (
    <div className="flex flex-col items-center justify-center relative p-2">
      <svg className="w-32 h-32 transform -rotate-90">
        {/* Background track */}
        <circle
          cx="64"
          cy="64"
          r={radius}
          className="stroke-slate-800"
          strokeWidth="8"
          fill="transparent"
        />
        {/* Animated Risk Score Arc */}
        <circle
          cx="64"
          cy="64"
          r={radius}
          stroke={style.stroke}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          fill="transparent"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-2xl font-extrabold text-white tracking-tight">
          {percentage}%
        </span>
        <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
          Risk Index
        </span>
      </div>
    </div>
  );
};
