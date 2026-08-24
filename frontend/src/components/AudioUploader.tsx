import React, { useRef, useState } from 'react';
import { UploadCloud, FileAudio, CheckCircle2, ShieldAlert, AlertTriangle, Sparkles } from 'lucide-react';
import { formatFileSize } from '../utils/audioUtils';
import { RiskStatus } from '../types/analysis';

interface AudioUploaderProps {
  onFileSelect: (file: File, presetStatus?: RiskStatus) => void;
  isAnalyzing: boolean;
}

export const AudioUploader: React.FC<AudioUploaderProps> = ({
  onFileSelect,
  isAnalyzing,
}) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  const handlePresetSelect = (name: string, type: RiskStatus) => {
    const dummyBlob = new Blob(['RIFF....WAVEfmt ....data....'], { type: 'audio/wav' });
    const dummyFile = new File([dummyBlob], `${name.toLowerCase().replace(/\s+/g, '_')}.wav`, { type: 'audio/wav' });
    setSelectedFile(dummyFile);
    onFileSelect(dummyFile, type);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
      
      {/* Header */}
      <div className="flex items-center space-x-2 mb-4">
        <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
          <UploadCloud className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-100 text-base">Audio File Upload & Presets</h3>
          <p className="text-xs text-slate-400">Drag & drop WAV, MP3, FLAC audio files or use demo samples</p>
        </div>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all ${
          isDragOver
            ? 'border-cyan-400 bg-cyan-500/10'
            : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/80'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          className="hidden"
          onChange={handleFileChange}
        />
        <div className="flex flex-col items-center justify-center py-2 space-y-2">
          <FileAudio className="w-8 h-8 text-cyan-400 opacity-80" />
          <p className="text-xs font-medium text-slate-300">
            {selectedFile ? (
              <span className="text-cyan-400 font-semibold">{selectedFile.name} ({formatFileSize(selectedFile.size)})</span>
            ) : (
              <span>Click to browse or drop audio file here</span>
            )}
          </p>
          <span className="text-[10px] text-slate-500">Supports WAV, MP3, FLAC, M4A up to 25MB</span>
        </div>
      </div>

      {/* Demo Preset Buttons for Quick Testing */}
      <div className="mt-4 pt-3 border-t border-slate-800/80">
        <div className="flex items-center space-x-1 mb-2 text-xs text-slate-400 font-medium">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Quick Demo Test Presets:</span>
        </div>
        <div className="grid grid-cols-3 gap-2">
          
          <button
            onClick={() => handlePresetSelect('Human Voice Sample', 'SAFE')}
            disabled={isAnalyzing}
            className="flex items-center justify-center space-x-1.5 p-2 rounded-xl bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-500/30 text-emerald-400 text-xs font-medium transition-all disabled:opacity-50"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Human (Safe)</span>
          </button>

          <button
            onClick={() => handlePresetSelect('Replay Reverberation', 'SUSPICIOUS')}
            disabled={isAnalyzing}
            className="flex items-center justify-center space-x-1.5 p-2 rounded-xl bg-amber-950/40 hover:bg-amber-900/60 border border-amber-500/30 text-amber-400 text-xs font-medium transition-all disabled:opacity-50"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Replay (Suspicious)</span>
          </button>

          <button
            onClick={() => handlePresetSelect('AI Voice Clone', 'HIGH_RISK')}
            disabled={isAnalyzing}
            className="flex items-center justify-center space-x-1.5 p-2 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 border border-rose-500/30 text-rose-400 text-xs font-medium transition-all disabled:opacity-50"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>AI Clone (High Risk)</span>
          </button>

        </div>
      </div>

    </div>
  );
};
