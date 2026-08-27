import React, { useState } from 'react';
import { AudioRecorder } from '../components/AudioRecorder';
import { AudioUploader } from '../components/AudioUploader';
import { ResultCard } from '../components/ResultCard';
import { useAudioAnalysis } from '../hooks/useAudioAnalysis';
import { RiskStatus } from '../types/analysis';
import { Loader2, Shield, Info, Mic, UploadCloud, Sparkles, CheckCircle2, AlertTriangle, ShieldAlert, Cpu, Radio, ShieldCheck } from 'lucide-react';
import { createDemoWavBlob } from '../utils/audioUtils';

interface DashboardProps {
  isMockMode: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({ isMockMode }) => {
  const {
    isAnalyzing,
    result,
    error,
    runAnalysis,
    resetAnalysis,
  } = useAudioAnalysis();

  const [activeInputTab, setActiveInputTab] = useState<'record' | 'upload'>('record');

  const handleAudioInput = (fileOrBlob: File | Blob, presetStatus?: RiskStatus) => {
    runAnalysis(fileOrBlob, presetStatus);
  };

  const handlePresetSelect = (name: string, type: RiskStatus) => {
    const freqMap: Record<RiskStatus, number> = {
      SAFE: 220,
      SUSPICIOUS: 880,
      HIGH_RISK: 1760
    };
    const validWavBlob = createDemoWavBlob(1.5, freqMap[type] || 440);
    const demoFile = new File([validWavBlob], `${name.toLowerCase().replace(/\s+/g, '_')}.wav`, { type: 'audio/wav' });
    runAnalysis(demoFile, type);
  };

  return (
    <div className="space-y-8 pb-12">
      
      {/* 1. Concise Professional Hero Section */}
      <div className="bg-slate-900/60 rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-[11px] uppercase tracking-widest font-extrabold text-cyan-400">VOXSHIELD</span>
            <h1 className="text-xl sm:text-2xl font-bold text-white mt-1">
              AI Voice Impersonation & Deepfake Security
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl">
              Detect synthetic voices and acoustic replay attacks using neural anti-spoofing and audio forensics.
            </p>
          </div>

          {/* Trust Status Line */}
          <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-400 shrink-0">
            <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1" />
              <span>Detection Engine Online</span>
            </span>
            <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800">
              <span>Neural + DSP Engine</span>
            </span>
          </div>
        </div>
      </div>

      {/* 2. Unified Analysis Workflow */}
      {!result && (
        <div className="bg-slate-900/80 rounded-2xl p-6 border border-slate-800 space-y-6">
          
          <div>
            <h2 className="text-base font-bold text-white">Analyze Voice</h2>
            <p className="text-xs text-slate-400 mt-0.5">Record a voice sample or upload an audio file for real-time security analysis.</p>
          </div>

          {/* Tab Selection: Record vs Upload */}
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-4">
            <button
              onClick={() => setActiveInputTab('record')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeInputTab === 'record'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-slate-800'
              }`}
            >
              <Mic className="w-4 h-4" />
              <span>Record Voice</span>
            </button>

            <button
              onClick={() => setActiveInputTab('upload')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeInputTab === 'upload'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-slate-800'
              }`}
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload Audio</span>
            </button>
          </div>

          {/* Input Component View */}
          <div>
            {activeInputTab === 'record' ? (
              <AudioRecorder onAudioReady={handleAudioInput} isAnalyzing={isAnalyzing} />
            ) : (
              <AudioUploader onFileSelect={handleAudioInput} isAnalyzing={isAnalyzing} />
            )}
          </div>

          {/* Demoted Offline Demo Samples */}
          <div className="pt-4 border-t border-slate-800/80">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
              <div>
                <span className="text-xs font-semibold text-slate-300">Demo Samples</span>
                <p className="text-[11px] text-slate-400">Offline demonstration only — not a live security analysis.</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <button
                onClick={() => handlePresetSelect('Human Voice Sample', 'SAFE')}
                disabled={isAnalyzing}
                className="flex items-center justify-center space-x-1.5 p-2 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-800 text-emerald-400 text-xs font-medium transition-all disabled:opacity-50"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Human (Demo)</span>
              </button>

              <button
                onClick={() => handlePresetSelect('Replay Reverberation', 'SUSPICIOUS')}
                disabled={isAnalyzing}
                className="flex items-center justify-center space-x-1.5 p-2 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-800 text-amber-400 text-xs font-medium transition-all disabled:opacity-50"
              >
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Replay (Demo)</span>
              </button>

              <button
                onClick={() => handlePresetSelect('AI Voice Clone', 'HIGH_RISK')}
                disabled={isAnalyzing}
                className="flex items-center justify-center space-x-1.5 p-2 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-800 text-rose-400 text-xs font-medium transition-all disabled:opacity-50"
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>AI Clone (Demo)</span>
              </button>
            </div>
          </div>

        </div>
      )}

      {/* 3. Analysis In Progress State */}
      {isAnalyzing && (
        <div className="bg-slate-900/90 rounded-2xl p-8 border border-slate-800 text-center flex flex-col items-center justify-center space-y-6">
          <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
          
          <div className="space-y-1">
            <h4 className="font-bold text-white text-base">ANALYZING AUDIO</h4>
            <p className="text-xs text-slate-400">Executing multi-signal neural anti-spoofing and acoustic replay analysis</p>
          </div>

          <div className="w-full max-w-md bg-slate-950 p-4 rounded-xl border border-slate-800 text-left text-xs space-y-2 font-mono">
            <div className="flex items-center justify-between text-emerald-400">
              <span>Audio payload received</span>
              <span>✓</span>
            </div>
            <div className="flex items-center justify-between text-emerald-400">
              <span>Audio normalization & resampling</span>
              <span>✓</span>
            </div>
            <div className="flex items-center justify-between text-cyan-400 animate-pulse">
              <span>Neural anti-spoofing inference</span>
              <span>●</span>
            </div>
            <div className="flex items-center justify-between text-slate-500">
              <span>Replay acoustic DSP analysis</span>
              <span>○</span>
            </div>
            <div className="flex items-center justify-between text-slate-500">
              <span>Multi-signal risk assessment</span>
              <span>○</span>
            </div>
          </div>
        </div>
      )}

      {/* 4. Error Message Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-3">
          <Info className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* 5. Analysis Results Display */}
      {result && !isAnalyzing && (
        <div className="transition-all duration-500">
          <ResultCard result={result} onReset={resetAnalysis} />
        </div>
      )}

      {/* 6. Security Engine Footer Info */}
      <footer className="pt-6 border-t border-slate-800/80 text-center text-xs text-slate-400 space-y-1">
        <p className="font-semibold text-slate-300">VoxShield Security Engine</p>
        <p>Neural anti-spoofing + Acoustic replay detection + Forensic risk assessment</p>
      </footer>

    </div>
  );
};
