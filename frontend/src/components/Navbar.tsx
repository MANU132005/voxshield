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
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="p-2 bg-gradient-to-tr from-cyan-500/20 to-blue-600/30 border border-cyan-500/40 rounded-xl shadow-lg shadow-cyan-500/10">
            <Shield className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
                VOXSHIELD
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-500/30">
                SIH AI
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">AI Voice Impersonation & Deepfake Detection</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'dashboard'
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'analytics'
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            API Docs & Specs
          </button>
        </nav>

        {/* Controls & Status Indicator */}
        <div className="flex items-center space-x-4">
          
          {/* Live Backend Status Badge */}
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <Activity className={`w-3.5 h-3.5 ${backendStatus === 'online' ? 'text-emerald-400 animate-pulse' : 'text-amber-500'}`} />
            <span className="text-slate-400">FastAPI:</span>
            <span className={`font-semibold ${backendStatus === 'online' ? 'text-emerald-400' : 'text-amber-400'}`}>
              {backendStatus === 'online' ? 'Online' : 'Mock Ready'}
            </span>
          </div>

          {/* Mock API Mode Toggle */}
          <button
            onClick={() => onToggleMockMode(!isMockMode)}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700/60 transition-all text-xs font-medium"
            title="Toggle between Frontend Mock Mode and Live FastAPI Backend"
          >
            {isMockMode ? (
              <ToggleRight className="w-5 h-5 text-cyan-400" />
            ) : (
              <ToggleLeft className="w-5 h-5 text-slate-500" />
            )}
            <span className="text-slate-300">
              Mode: <span className={isMockMode ? 'text-cyan-400 font-bold' : 'text-emerald-400 font-bold'}>
                {isMockMode ? 'Mock API' : 'FastAPI Live'}
              </span>
            </span>
          </button>

        </div>
      </div>
    </header>
  );
};
