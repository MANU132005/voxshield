import React from 'react';
import { Shield, Activity, Wifi, WifiOff, Terminal, ShieldAlert, Cpu } from 'lucide-react';
import { HealthCheckResult } from '../../api/healthApi';

interface HeaderProps {
  health: HealthCheckResult | null;
  isCheckingHealth: boolean;
  onRefreshHealth: () => void;
  activeTab: string;
  onSelectTab: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  isCheckingHealth,
  onRefreshHealth,
  activeTab,
  onSelectTab,
}) => {
  const isOnline = health?.isOnline ?? false;
  const latency = health?.latencyMs ?? 0;

  return (
    <header className="sticky top-0 z-50 bg-[#2F4156] border-b border-[#263546] shadow-md px-4 lg:px-8 py-3.5 text-white">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand identity */}
        <div
          className="flex items-center space-x-3.5 cursor-pointer group"
          onClick={() => onSelectTab('dashboard')}
        >
          <div className="p-2.5 bg-[#567C8D]/40 border border-[#C8D9E6]/30 rounded-2xl shadow-sm group-hover:border-[#C8D9E6] transition-all duration-300">
            <Shield className="w-6 h-6 text-[#C8D9E6] group-hover:scale-105 transition-transform" />
          </div>
          <div>
            <div className="flex items-center space-x-2.5">
              <span className="font-black text-xl tracking-tight text-white font-sans">
                VOXSHIELD
              </span>
              <span className="text-[10px] uppercase font-mono font-bold tracking-widest px-2 py-0.5 rounded-full bg-[#567C8D] text-white border border-[#C8D9E6]/30">
                SOC CONSOLE
              </span>
            </div>
            <p className="text-[11px] text-[#C8D9E6] hidden sm:block font-medium">
              AI Voice Impersonation & Deepfake Defense System
            </p>
          </div>
        </div>

        {/* Live Backend Telemetry Indicator */}
        <div className="flex items-center space-x-3">
          
          <button
            onClick={onRefreshHealth}
            disabled={isCheckingHealth}
            title="FastAPI Backend Health & Inference Status (Click to ping)"
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-xl border text-xs font-mono transition-all ${
              isOnline
                ? 'bg-[#263546] border-emerald-400/40 text-emerald-300 hover:border-emerald-300'
                : 'bg-rose-950/70 border-rose-400/40 text-rose-200 hover:border-rose-300'
            }`}
          >
            <div className="relative flex items-center justify-center">
              <span
                className={`w-2 h-2 rounded-full ${
                  isOnline ? 'bg-emerald-400 animate-ping absolute' : 'bg-rose-500'
                }`}
              />
              <span
                className={`w-2 h-2 rounded-full ${
                  isOnline ? 'bg-emerald-400' : 'bg-rose-500'
                }`}
              />
            </div>
            <span className="font-semibold">{isOnline ? 'FASTAPI LIVE' : 'BACKEND OFFLINE'}</span>
            {isOnline && (
              <span className="text-[#C8D9E6] border-l border-[#567C8D]/60 pl-2">
                {latency}ms
              </span>
            )}
          </button>

          {/* SIH 2026 Badge */}
          <div className="hidden lg:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-[#263546] border border-[#567C8D]/50 text-[11px] text-[#C8D9E6] font-mono">
            <Cpu className="w-3.5 h-3.5 text-[#C8D9E6]" />
            <span>SIH26104</span>
          </div>

        </div>
      </div>
    </header>
  );
};

