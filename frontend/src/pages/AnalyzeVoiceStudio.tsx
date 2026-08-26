import React from 'react';
import { Shield, Sparkles, SearchCode, Lock, RotateCcw, ArrowRight, Activity, FileCheck2 } from 'lucide-react';
import { AudioRecorder } from '../components/analysis/AudioRecorder';
import { AudioUploader } from '../components/analysis/AudioUploader';
import { ProcessingPipeline } from '../components/analysis/ProcessingPipeline';
import { DecisionHero } from '../components/decision/DecisionHero';
import { SignalGrid } from '../components/decision/SignalGrid';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { EnrichedAnalysisResult, ApiError } from '../api/types';

interface AnalyzeVoiceStudioProps {
  isAnalyzing: boolean;
  activeResult: EnrichedAnalysisResult | null;
  error: ApiError | string | null;
  onAnalyzeAudio: (
    fileOrBlob: File | Blob,
    metadata: {
      name: string;
      sizeBytes: number;
      mimeType?: string;
      durationSeconds?: number;
      source: 'MICROPHONE' | 'FILE_UPLOAD';
    }
  ) => void;
  onResetAnalysis: () => void;
  onNavigateToForensics: () => void;
}

export const AnalyzeVoiceStudio: React.FC<AnalyzeVoiceStudioProps> = ({
  isAnalyzing,
  activeResult,
  error,
  onAnalyzeAudio,
  onResetAnalysis,
  onNavigateToForensics,
}) => {
  const handleMicrophoneAudio = (
    blob: Blob,
    metadata: { name: string; sizeBytes: number; durationSeconds: number; source: 'MICROPHONE' }
  ) => {
    onAnalyzeAudio(blob, {
      name: metadata.name,
      sizeBytes: metadata.sizeBytes,
      mimeType: blob.type || 'audio/wav',
      durationSeconds: metadata.durationSeconds,
      source: 'MICROPHONE',
    });
  };

  const handleUploadedAudio = (
    file: File,
    metadata: { name: string; sizeBytes: number; durationSeconds?: number; source: 'FILE_UPLOAD' }
  ) => {
    onAnalyzeAudio(file, {
      name: metadata.name,
      sizeBytes: metadata.sizeBytes,
      mimeType: file.type || 'audio/wav',
      durationSeconds: metadata.durationSeconds,
      source: 'FILE_UPLOAD',
    });
  };

  return (
    <div className="space-y-8 pb-12 animate-in fade-in duration-300">
      
      {/* 1. Header & Studio Overview Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#C8D9E6]/60 pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] text-[10px] font-mono font-bold">
              HERO AUDIT STUDIO
            </span>
            <span className="text-[11px] text-[#567C8D] font-mono font-medium">POST /api/v1/analyze</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#2F4156] tracking-tight mt-1">
            Voice Impersonation Analysis Studio
          </h1>
          <p className="text-xs sm:text-sm text-[#567C8D] mt-0.5">
            Capture live microphone phonation or upload audio files to test against dual AI anti-spoofing and replay DSP classifiers.
          </p>
        </div>

        {activeResult && (
          <button
            onClick={onResetAnalysis}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-[#F5F2EB] hover:bg-white border border-[#C8D9E6] hover:border-[#567C8D] text-xs font-semibold text-[#2F4156] transition-all shrink-0 font-medium"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#567C8D]" />
            <span>New Voice Audit</span>
          </button>
        )}
      </div>

      {/* 2. Privacy & Ephemeral Data Note */}
      <div className="p-3.5 rounded-2xl bg-[#F5F2EB] border border-[#C8D9E6] flex items-center justify-between text-xs text-[#567C8D]">
        <div className="flex items-center space-x-2.5">
          <Lock className="w-4 h-4 text-[#567C8D] shrink-0" />
          <span>
            <strong className="text-[#2F4156]">Zero Retention Policy:</strong> Audio buffers are processed strictly in-memory by the FastAPI risk engine and immediately cleared.
          </span>
        </div>
        <span className="hidden sm:inline font-mono text-[10px] text-[#567C8D]">
          Max Payload: 15MB
        </span>
      </div>

      {/* 3. Input Controls (Always visible or customizable) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AudioRecorder
          onAudioReady={handleMicrophoneAudio}
          isAnalyzing={isAnalyzing}
        />
        <AudioUploader
          onFileSelect={handleUploadedAudio}
          isAnalyzing={isAnalyzing}
        />
      </div>

      {/* 4. Processing Pipeline State */}
      {isAnalyzing && (
        <div className="transition-all duration-300">
          <ProcessingPipeline />
        </div>
      )}

      {/* 5. Error Alert with Retry */}
      {error && !isAnalyzing && (
        <ErrorAlert
          error={error}
          onRetry={onResetAnalysis}
        />
      )}

      {/* 6. HERO Analysis Result Screen */}
      {activeResult && !isAnalyzing && (
        <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
          
          {/* Main Decision Hero */}
          <DecisionHero enrichedResult={activeResult} />

          {/* AI vs Replay Signal Grid */}
          <SignalGrid response={activeResult.raw} />

          {/* Deep-Dive Action Card to Forensic Inspector */}
          <div className="bg-white rounded-2xl p-5 border border-[#C8D9E6] shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3.5">
              <div className="p-2.5 rounded-xl bg-[#C8D9E6]/40 border border-[#C8D9E6] text-[#2F4156]">
                <SearchCode className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-[#2F4156]">
                  Inspect Forensic Evidence & Processing Timeline
                </h4>
                <p className="text-xs text-[#567C8D] mt-0.5">
                  View full diagnostic reasons ({activeResult.evidenceList.length}), counter-evidence ({activeResult.counterEvidenceList.length}), attack hypotheses ({activeResult.attackHypotheses.length}), and 10-stage execution timeline.
                </p>
              </div>
            </div>

            <button
              onClick={onNavigateToForensics}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-[#2F4156] hover:bg-[#19232f] text-white font-bold text-xs shadow-sm transition-all shrink-0"
            >
              <span>Open Forensic Inspector</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

        </div>
      )}

    </div>
  );
};

