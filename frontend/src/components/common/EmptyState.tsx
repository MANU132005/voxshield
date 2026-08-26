import React from 'react';
import { LucideIcon, Inbox } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  badgeText?: string;
  actionButton?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = Inbox,
  badgeText,
  actionButton,
  className = '',
}) => {
  return (
    <div
      className={`bg-white rounded-2xl p-8 border border-[#C8D9E6] shadow-xs text-center flex flex-col items-center justify-center space-y-3 ${className}`}
    >
      <div className="p-3.5 rounded-2xl bg-[#F5F2EB] border border-[#C8D9E6] text-[#567C8D] shadow-xs">
        <Icon className="w-8 h-8 opacity-80" />
      </div>

      {badgeText && (
        <span className="px-2.5 py-0.5 rounded-full bg-[#C8D9E6]/40 border border-[#C8D9E6] text-[10px] uppercase font-mono font-bold tracking-wider text-[#2F4156]">
          {badgeText}
        </span>
      )}

      <div className="max-w-md space-y-1">
        <h4 className="font-bold text-[#2F4156] text-sm">{title}</h4>
        <p className="text-xs text-[#567C8D] leading-relaxed">{description}</p>
      </div>

      {actionButton && <div className="pt-2">{actionButton}</div>}
    </div>
  );
};

