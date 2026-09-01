import React, { useEffect, useState } from 'react';
import { Shield, ToggleLeft, ToggleRight, Activity, Terminal } from 'lucide-react';
import { checkHealth } from '../services/api';

interface NavbarProps {
  isMockMode: boolean;
  onToggleMockMode: (value: boolean) => void;
  activeTab: 'dashboard' | 'analytics';
  setActiveTab: (tab: 'dashboard' | 'analytics') => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  isMockMode,
  onToggleMockMode,
  activeTab,
  setActiveTab
}) => {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const pingBackend = async () => {
      const res = await checkHealth();
      setBackendStatus(res.status === 'ok' ? 'online' : 'offline');
    };
    pingBackend();
    const interval = setInterval(pingBackend, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-50 bg-[#0b1329]/90 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="p-2 bg-slate-900 border border-slate-700/80 rounded-xl">
            <Shield className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight text-white">
                VOXSHIELD
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-500/30">
                AI SECURITY
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">AI Voice Impersonation & Deepfake Detection</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'dashboard'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'analytics'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            Developer / API
          </button>
        </nav>

        {/* Controls & Status Indicator */}
        <div className="flex items-center space-x-3">
          
          {/* Live Backend Status Badge */}
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
            <Activity className={`w-3.5 h-3.5 ${backendStatus === 'online' ? 'text-emerald-400 animate-pulse' : 'text-amber-500'}`} />
            <span className="text-slate-400">Backend:</span>
            <span className={`font-semibold ${backendStatus === 'online' ? 'text-emerald-400' : 'text-amber-400'}`}>
              {backendStatus === 'online' ? 'Online' : backendStatus === 'checking' ? 'Connecting...' : 'Standby'}
            </span>
          </div>

        </div>
      </div>
    </header>
  );
};
