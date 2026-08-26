import React, { useState } from 'react';
import { Copy, Check, Hash } from 'lucide-react';

interface RequestIdCopyProps {
  requestId: string;
  className?: string;
}

export const RequestIdCopy: React.FC<RequestIdCopyProps> = ({ requestId, className = '' }) => {
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(requestId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard', err);
    }
  };

  return (
    <button
      onClick={handleCopy}
      type="button"
      className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-[#F5F2EB] hover:bg-white border border-[#C8D9E6] hover:border-[#567C8D] text-[11px] font-mono text-[#2F4156] transition-all shadow-2xs ${className}`}
      title="Click to copy Request ID"
    >
      <Hash className="w-3 h-3 text-[#567C8D] shrink-0" />
      <span className="truncate max-w-[140px] sm:max-w-[200px] font-medium">{requestId}</span>
      {copied ? (
        <Check className="w-3 h-3 text-emerald-600 shrink-0" />
      ) : (
        <Copy className="w-3 h-3 text-[#567C8D] hover:text-[#2F4156] shrink-0" />
      )}
    </button>
  );
};

