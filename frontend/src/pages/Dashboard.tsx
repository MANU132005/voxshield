import React from 'react';
import { AudioRecorder } from '../components/AudioRecorder';
import { AudioUploader } from '../components/AudioUploader';
import { ResultCard } from '../components/ResultCard';
import { useAudioAnalysis } from '../hooks/useAudioAnalysis';
import { RiskStatus } from '../types/analysis';
import { Loader2, Shield, Info } from 'lucide-react';

interface DashboardProps {
  isMockMode: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({ isMockMode }) => {
  const {
    isAnalyzing,
    result,
    error,
    runAnalysis,
  } = useAudioAnalysis();

  const handleAudioInput = (fileOrBlob: File | Blob, presetStatus?: RiskStatus) => {
    runAnalysis(fileOrBlob, presetStatus);
  };

  return (
    <div className="space-y-8 pb-12">
      
      {/* Hero Welcome Banner */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 bg-gradient-to-br from-slate-900/90 via-slate-900/40 to-cyan-950/20 relative overflow-hidden">
        <div className="max-w-3xl space-y-3 relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold">
            <Shield className="w-3.5 h-3.5" />
            <span>SIH Hackathon Security Suite</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            AI Voice Impersonation & Deepfake Security Center
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            Record live speech or upload an audio file to evaluate synthetic AI voice cloning probability and physical acoustic replay attack risks in real-time.
          </p>
        </div>
      </div>

      {/* Main Grid: Input Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AudioRecorder onAudioReady={handleAudioInput} isAnalyzing={isAnalyzing} />
        <AudioUploader onFileSelect={handleAudioInput} isAnalyzing={isAnalyzing} />
      </div>

      {/* Loading Overlay State */}
      {isAnalyzing && (
        <div className="glass-panel rounded-2xl p-8 border border-slate-800 text-center flex flex-col items-center justify-center space-y-4">
          <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
          <div>
            <h4 className="font-semibold text-slate-100 text-base">Running Acoustic & AI Anti-Spoofing Analysis...</h4>
            <p className="text-xs text-slate-400 mt-1">Extracting LFCC spectral features & evaluating replay reverberation</p>
          </div>
        </div>
      )}

      {/* Error Message Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-3">
          <Info className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Analysis Results Display */}
      {result && !isAnalyzing && (
        <div className="transition-all duration-500">
          <ResultCard result={result} />
        </div>
      )}

    </div>
  );
};
