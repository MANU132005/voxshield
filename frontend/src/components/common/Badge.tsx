import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, Shield, CheckCircle2, XCircle, Info } from 'lucide-react';
import { BackendRiskStatus, SecurityDecision } from '../../api/types';

interface BadgeProps {
  variant: BackendRiskStatus | SecurityDecision | 'INFO' | 'NEUTRAL';
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant,
  size = 'md',
  showIcon = true,
  className = '',
}) => {
  let label = variant as string;
  let bgClass = 'bg-[#C8D9E6]/40 text-[#2F4156] border-[#C8D9E6]';
  let Icon = Shield;

  switch (variant) {
    case 'SAFE':
    case 'ALLOW':
      label = variant === 'ALLOW' ? 'DECISION: ALLOW' : 'STATUS: SAFE';
      bgClass = 'bg-emerald-50 text-emerald-800 border-emerald-300 shadow-sm';
      Icon = ShieldCheck;
      break;

    case 'SUSPICIOUS':
    case 'STEP-UP':
      label = variant === 'STEP-UP' ? 'DECISION: STEP-UP' : 'STATUS: SUSPICIOUS';
      bgClass = 'bg-amber-50 text-amber-800 border-amber-300 shadow-sm';
      Icon = AlertTriangle;
      break;

    case 'HIGH_RISK':
    case 'BLOCK':
      label = variant === 'BLOCK' ? 'DECISION: BLOCK' : 'STATUS: HIGH RISK';
      bgClass = 'bg-rose-50 text-rose-800 border-rose-300 shadow-sm';
      Icon = ShieldAlert;
      break;

    case 'INCONCLUSIVE':
      label = 'DECISION: INCONCLUSIVE';
      bgClass = 'bg-[#F5F2EB] text-[#2F4156] border-[#C8D9E6]';
      Icon = Info;
      break;

    case 'INFO':
      label = 'INFO';
      bgClass = 'bg-[#C8D9E6]/40 text-[#2F4156] border-[#567C8D]/40';
      Icon = Info;
      break;
  }

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 space-x-1 font-mono tracking-wider',
    md: 'text-xs px-2.5 py-1 space-x-1.5 font-semibold tracking-wide',
    lg: 'text-sm px-3.5 py-1.5 space-x-2 font-bold tracking-wider',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border uppercase select-none ${sizeClasses[size]} ${bgClass} ${className}`}
    >
      {showIcon && <Icon className={`${iconSizes[size]} shrink-0`} />}
      <span>{label}</span>
    </span>
  );
};

