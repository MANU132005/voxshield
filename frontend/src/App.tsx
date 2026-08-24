import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { Analytics } from './pages/Analytics';

export const App: React.FC = () => {
  const [isMockMode, setIsMockMode] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analytics'>('dashboard');

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col justify-between selection:bg-cyan-500 selection:text-white">
      
      <div>
        {/* Glassmorphism Header */}
        <Navbar
          isMockMode={isMockMode}
          onToggleMockMode={setIsMockMode}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        {/* Main Content Area */}
        <main className="max-w-7xl mx-auto px-4 lg:px-8 pt-8">
          {activeTab === 'dashboard' ? (
            <Dashboard isMockMode={isMockMode} />
          ) : (
            <Analytics />
          )}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between space-y-2 sm:space-y-0">
          <p>© 2026 VoxShield AI - Smart India Hackathon Project</p>
          <p className="flex items-center space-x-2">
            <span>Dev 1: Backend/AI</span>
            <span>•</span>
            <span>Dev 2: Frontend/UX</span>
          </p>
        </div>
      </footer>

    </div>
  );
};

export default App;
