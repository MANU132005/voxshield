import React from 'react';
import { LayoutDashboard, Mic2, SearchCode, Terminal, FileCode2 } from 'lucide-react';

export type NavTabId = 'dashboard' | 'analyze' | 'forensics' | 'specs';

interface TabNavProps {
  activeTab: NavTabId;
  onSelectTab: (tab: NavTabId) => void;
  hasActiveResult: boolean;
}

export const TabNav: React.FC<TabNavProps> = ({
  activeTab,
  onSelectTab,
  hasActiveResult,
}) => {
  const tabs = [
    {
      id: 'dashboard' as NavTabId,
      label: 'Security Center',
      icon: LayoutDashboard,
      description: 'System overview & posture',
    },
    {
      id: 'analyze' as NavTabId,
      label: 'Analyze Voice',
      icon: Mic2,
      description: 'Live mic & file audit studio',
    },
    {
      id: 'forensics' as NavTabId,
      label: 'Forensic Inspector',
      icon: SearchCode,
      description: 'Deep-dive evidence & timeline',
      badge: hasActiveResult ? 'Active Audit' : undefined,
    },
    {
      id: 'specs' as NavTabId,
      label: 'API Specs & System',
      icon: FileCode2,
      description: 'OpenAPI contracts & limits',
    },
  ];

  return (
    <div className="border-b border-[#263546] bg-[#2F4156] px-4 lg:px-8 shadow-inner">
      <div className="max-w-7xl mx-auto flex items-center space-x-2 sm:space-x-3 overflow-x-auto py-2 no-scrollbar">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              className={`flex items-center space-x-2.5 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all duration-200 ${
                isActive
                  ? 'bg-[#567C8D] text-white shadow-md border border-[#C8D9E6]/30'
                  : 'text-[#C8D9E6] hover:text-white hover:bg-[#3a516b] border border-transparent'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-[#C8D9E6]'}`} />
              <span>{tab.label}</span>
              {tab.badge && (
                <span className="px-2 py-0.5 rounded-full bg-[#C8D9E6] text-[#2F4156] text-[10px] font-mono font-bold shadow-sm">
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

