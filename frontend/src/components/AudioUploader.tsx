import React, { useRef, useState } from 'react';
import { UploadCloud, FileAudio, CheckCircle2, ShieldAlert, AlertTriangle, Sparkles } from 'lucide-react';
import { formatFileSize, createDemoWavBlob } from '../utils/audioUtils';
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

  return (
    <div className="bg-slate-900/60 rounded-2xl p-6 border border-slate-800 flex flex-col justify-between h-full">
      
      {/* Header */}
      <div className="flex items-center space-x-2 mb-4">
        <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
          <UploadCloud className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-100 text-sm">Upload Audio File</h3>
          <p className="text-xs text-slate-400">Select or drop a voice file for analysis</p>
        </div>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all flex-1 flex flex-col justify-center items-center ${
          isDragOver
            ? 'border-cyan-400 bg-cyan-500/10'
            : 'border-slate-800 hover:border-slate-700 bg-slate-950/40 hover:bg-slate-950/80'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          className="hidden"
          onChange={handleFileChange}
        />
        <div className="flex flex-col items-center justify-center space-y-2 py-3">
          <FileAudio className="w-8 h-8 text-cyan-400 opacity-90" />
          <p className="text-xs font-medium text-slate-200">
            {selectedFile ? (
              <span className="text-cyan-400 font-semibold">{selectedFile.name} ({formatFileSize(selectedFile.size)})</span>
            ) : (
              <span>Click to browse or drop audio file here</span>
            )}
          </p>
          <div className="text-[11px] text-slate-400 space-y-0.5">
            <p>Supported formats: <strong className="text-slate-300">WAV, MP3, FLAC, M4A</strong></p>
            <p>Maximum file size: <strong className="text-slate-300">25 MB</strong></p>
          </div>
        </div>
      </div>

    </div>
  );
};
