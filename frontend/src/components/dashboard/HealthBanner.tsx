import React from 'react';
import { Activity, Server, Shield, Wifi, WifiOff, FileCode, CheckCircle2, RotateCcw } from 'lucide-react';
import { HealthCheckResult } from '../../api/healthApi';
import { API_BASE_URL, API_V1_URL } from '../../api/client';

interface HealthBannerProps {
  health: HealthCheckResult | null;
  isChecking: boolean;
  onRefresh: () => void;
}

export const HealthBanner: React.FC<HealthBannerProps> = ({
  health,
  isChecking,
  onRefresh,
}) => {
  const isOnline = health?.isOnline ?? false;
  const latency = health?.latencyMs ?? 0;

  return (
    <div
      className={`bg-white rounded-3xl p-6 border ${
        isOnline ? 'border-emerald-300' : 'border-rose-300'
      } shadow-sm relative overflow-hidden`}
    >
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
        
        {/* Left: Core Status Details */}
        <div className="flex items-start space-x-4">
          <div
            className={`p-3.5 rounded-2xl border shrink-0 ${
              isOnline
                ? 'bg-emerald-50 border-emerald-200 text-emerald-700 shadow-xs'
                : 'bg-rose-50 border-rose-200 text-rose-700 shadow-xs'
            }`}
          >
            {isOnline ? <Server className="w-7 h-7" /> : <WifiOff className="w-7 h-7" />}
          </div>

          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xl font-extrabold text-[#2F4156] tracking-tight">
                {isOnline ? 'VoxShield AI Gateway Operational' : 'Backend Gateway Offline'}
              </h2>
              <span
                className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase border ${
                  isOnline
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                    : 'bg-rose-50 text-rose-800 border-rose-300'
                }`}
              >
                {isOnline ? 'HEALTHY' : 'UNREACHABLE'}
              </span>
            </div>

            <p className="text-xs text-[#567C8D] max-w-2xl leading-relaxed">
              {isOnline
                ? 'FastAPI anti-spoofing engine & DSP replay pipeline are active and accepting audio inference requests.'
                : 'Could not connect to FastAPI server at http://localhost:8000. Start backend using `uvicorn app.main:app --reload`.'}
            </p>
          </div>
        </div>

        {/* Right: Quick Action & Endpoint Details */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={onRefresh}
            disabled={isChecking}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-[#F5F2EB] hover:bg-white border border-[#C8D9E6] hover:border-[#567C8D] text-xs font-mono text-[#2F4156] transition-all disabled:opacity-50 font-medium"
          >
            <RotateCcw className={`w-3.5 h-3.5 text-[#567C8D] ${isChecking ? 'animate-spin' : ''}`} />
            <span>Ping Gateway</span>
          </button>

          <a
            href={`${API_V1_URL}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-[#567C8D] hover:bg-[#476878] text-white border border-[#2F4156] text-xs font-mono font-medium shadow-xs transition-all"
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>OpenAPI Docs</span>
          </a>
        </div>

      </div>

      {/* Mini Telemetry Bar */}
      <div className="mt-5 pt-4 border-t border-[#C8D9E6]/60 flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono text-[#567C8D]">
        <div className="flex items-center space-x-4">
          <span>Endpoint: <strong className="text-[#2F4156]">{API_V1_URL}</strong></span>
          <span>&bull;</span>
          <span>Roundtrip: <strong className={isOnline ? 'text-emerald-700' : 'text-rose-700'}>{latency}ms</strong></span>
        </div>
        <div>
          <span>Security Protocol: <strong className="text-[#2F4156]">ClaimGuard v1.0</strong></span>
        </div>
      </div>
    </div>
  );
};

