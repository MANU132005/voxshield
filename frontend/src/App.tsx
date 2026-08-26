import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/layout/Header';
import { TabNav, NavTabId } from './components/layout/TabNav';
import { Footer } from './components/layout/Footer';
import { SecurityDashboard } from './pages/SecurityDashboard';
import { AnalyzeVoiceStudio } from './pages/AnalyzeVoiceStudio';
import { ForensicInspector } from './pages/ForensicInspector';
import { SystemArchitecture } from './pages/SystemArchitecture';
import { useAudioAnalysis } from './hooks/useAudioAnalysis';
import { checkBackendHealth, HealthCheckResult } from './api/healthApi';
import { SessionAuditRecord } from './api/types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTabId>('dashboard');
  const [health, setHealth] = useState<HealthCheckResult | null>(null);
  const [isCheckingHealth, setIsCheckingHealth] = useState<boolean>(false);

  const {
    isAnalyzing,
    activeResult,
    error,
    sessionRecords,
    runAnalysis,
    selectRecord,
    resetAnalysis,
    clearSession,
  } = useAudioAnalysis();

  const pingHealth = useCallback(async () => {
    setIsCheckingHealth(true);
    try {
      const res = await checkBackendHealth();
      setHealth(res);
    } catch (err) {
      console.error('Failed to ping backend', err);
    } finally {
      setIsCheckingHealth(false);
    }
  }, []);

  useEffect(() => {
    pingHealth();
    const interval = setInterval(pingHealth, 15000); // Poll health every 15 seconds
    return () => clearInterval(interval);
  }, [pingHealth]);

  const handleSelectRecord = (record: SessionAuditRecord) => {
    selectRecord(record);
    setActiveTab('analyze');
  };

  const handleNavigateToAnalyze = () => {
    setActiveTab('analyze');
  };

  const handleNavigateToForensics = () => {
    setActiveTab('forensics');
  };

  return (
    <div className="min-h-screen bg-[#F5F2EB] text-[#2F4156] flex flex-col justify-between selection:bg-[#567C8D] selection:text-white font-sans">
      
      <div>
        {/* Top SOC Console Header */}
        <Header
          health={health}
          isCheckingHealth={isCheckingHealth}
          onRefreshHealth={pingHealth}
          activeTab={activeTab}
          onSelectTab={(tab) => setActiveTab(tab as NavTabId)}
        />

        {/* Navigation Switcher */}
        <TabNav
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          hasActiveResult={!!activeResult}
        />

        {/* Main Routed Content Area */}
        <main className="max-w-7xl mx-auto px-4 lg:px-8 pt-8">
          {activeTab === 'dashboard' && (
            <SecurityDashboard
              health={health}
              isCheckingHealth={isCheckingHealth}
              onRefreshHealth={pingHealth}
              sessionRecords={sessionRecords}
              onSelectRecord={handleSelectRecord}
              onNavigateToAnalyze={handleNavigateToAnalyze}
              onClearSession={clearSession}
            />
          )}

          {activeTab === 'analyze' && (
            <AnalyzeVoiceStudio
              isAnalyzing={isAnalyzing}
              activeResult={activeResult}
              error={error}
              onAnalyzeAudio={runAnalysis}
              onResetAnalysis={resetAnalysis}
              onNavigateToForensics={handleNavigateToForensics}
            />
          )}

          {activeTab === 'forensics' && (
            <ForensicInspector
              activeResult={activeResult}
              onNavigateToAnalyze={handleNavigateToAnalyze}
            />
          )}

          {activeTab === 'specs' && (
            <SystemArchitecture />
          )}
        </main>
      </div>

      {/* Security Console Footer */}
      <Footer />

    </div>
  );
};

export default App;
