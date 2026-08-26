import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  accentColor?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'purple' | 'slate';
  badge?: string;
  trend?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  accentColor = 'cyan',
  badge,
  trend,
}) => {
  const colorMap = {
    cyan: {
      border: 'border-[#C8D9E6] hover:border-[#567C8D]',
      iconBg: 'bg-[#C8D9E6]/40 border-[#C8D9E6] text-[#2F4156]',
      text: 'text-[#567C8D]',
    },
    emerald: {
      border: 'border-[#C8D9E6] hover:border-emerald-500/50',
      iconBg: 'bg-emerald-50 border-emerald-200 text-emerald-700',
      text: 'text-emerald-700',
    },
    amber: {
      border: 'border-[#C8D9E6] hover:border-amber-500/50',
      iconBg: 'bg-amber-50 border-amber-200 text-amber-700',
      text: 'text-amber-700',
    },
    rose: {
      border: 'border-[#C8D9E6] hover:border-rose-500/50',
      iconBg: 'bg-rose-50 border-rose-200 text-rose-700',
      text: 'text-rose-700',
    },
    purple: {
      border: 'border-[#C8D9E6] hover:border-[#567C8D]',
      iconBg: 'bg-[#C8D9E6]/50 border-[#C8D9E6] text-[#2F4156]',
      text: 'text-[#2F4156]',
    },
    slate: {
      border: 'border-[#C8D9E6] hover:border-[#567C8D]',
      iconBg: 'bg-[#F5F2EB] border-[#C8D9E6] text-[#567C8D]',
      text: 'text-[#567C8D]',
    },
  };

  const scheme = colorMap[accentColor] || colorMap.cyan;

  return (
    <div
      className={`bg-white rounded-2xl p-5 border ${scheme.border} shadow-sm hover:shadow-md transition-all relative overflow-hidden group`}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-semibold text-[#567C8D] uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-extrabold text-[#2F4156] tracking-tight font-mono">{value}</p>
        </div>
        <div className={`p-2.5 rounded-xl border ${scheme.iconBg} shadow-xs`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {(subtitle || badge || trend) && (
        <div className="mt-3 pt-3 border-t border-[#C8D9E6]/60 flex items-center justify-between text-xs">
          {subtitle && <span className="text-[#567C8D]">{subtitle}</span>}
          {badge && (
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold border ${scheme.iconBg}`}>
              {badge}
            </span>
          )}
          {trend && <span className={`font-mono text-[11px] font-semibold ${scheme.text}`}>{trend}</span>}
        </div>
      )}
    </div>
  );
};

