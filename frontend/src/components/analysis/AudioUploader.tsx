import React, { useRef, useState } from 'react';
import { UploadCloud, FileAudio, AlertCircle, Send, CheckCircle2, ShieldAlert, AlertTriangle, FileSpreadsheet, RotateCcw } from 'lucide-react';
import { formatFileSize, validateAudioFile, getAudioDuration } from '../../utils/audioUtils';
import { AudioPlayerBar } from './AudioPlayerBar';

interface AudioUploaderProps {
  onFileSelect: (
    file: File,
    metadata: { name: string; sizeBytes: number; durationSeconds?: number; source: 'FILE_UPLOAD' }
  ) => void;
  isAnalyzing: boolean;
}

export const AudioUploader: React.FC<AudioUploaderProps> = ({
  onFileSelect,
  isAnalyzing,
}) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [duration, setDuration] = useState<number | undefined>(undefined);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const processFile = async (file: File) => {
    setValidationError(null);
    const validation = validateAudioFile(file);
    if (!validation.isValid) {
      setValidationError(validation.error || 'Invalid audio file.');
      return;
    }

    setSelectedFile(file);
    try {
      const dur = await getAudioDuration(file);
      setDuration(dur);
    } catch (e) {
      setDuration(undefined);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setDuration(undefined);
    setValidationError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = () => {
    if (!selectedFile) return;
    onFileSelect(selectedFile, {
      name: selectedFile.name,
      sizeBytes: selectedFile.size,
      durationSeconds: duration,
      source: 'FILE_UPLOAD',
    });
  };

  /**
   * Helper to create a compliant synthetic WAV buffer for test bench demonstration.
   */
  const handleLoadTestSample = (sampleName: string, frequencyHz: number = 440) => {
    // Generate valid 16kHz Mono 16-bit PCM WAV in memory
    const sampleRate = 16000;
    const durationSec = 3.0;
    const numSamples = Math.floor(sampleRate * durationSec);
    const buffer = new ArrayBuffer(44 + numSamples * 2);
    const view = new DataView(buffer);

    // RIFF chunk descriptor
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + numSamples * 2, true);
    writeString(view, 8, 'WAVE');

    // fmt sub-chunk
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
    view.setUint16(20, 1, true); // AudioFormat (1 for PCM)
    view.setUint16(22, 1, true); // NumChannels (1 mono)
    view.setUint32(24, sampleRate, true); // SampleRate
    view.setUint32(28, sampleRate * 2, true); // ByteRate
    view.setUint16(32, 2, true); // BlockAlign
    view.setUint16(34, 16, true); // BitsPerSample (16-bit)

    // data sub-chunk
    writeString(view, 36, 'data');
    view.setUint32(40, numSamples * 2, true);

    // Write synthesized sine tone with harmonic decay
    for (let i = 0; i < numSamples; i++) {
      const t = i / sampleRate;
      const amplitude = Math.sin(2 * Math.PI * frequencyHz * t) * 0.5 +
                        Math.sin(2 * Math.PI * (frequencyHz * 2) * t) * 0.25;
      const sample = Math.max(-1, Math.min(1, amplitude)) * 0x7FFF;
      view.setInt16(44 + i * 2, sample, true);
    }

    const blob = new Blob([buffer], { type: 'audio/wav' });
    const file = new File([blob], `${sampleName.toLowerCase().replace(/\s+/g, '_')}.wav`, {
      type: 'audio/wav',
    });

    processFile(file);
  };

  const writeString = (view: DataView, offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm flex flex-col justify-between space-y-4">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="p-2.5 rounded-xl bg-[#C8D9E6]/40 border border-[#C8D9E6] text-[#2F4156]">
          <UploadCloud className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-bold text-[#2F4156] text-sm sm:text-base">Audio File Ingestion</h3>
          <p className="text-[11px] text-[#567C8D]">Upload WAV, MP3, FLAC, M4A, OGG samples up to 15MB</p>
        </div>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-200 ${
          isDragOver
            ? 'border-[#567C8D] bg-[#C8D9E6]/30 shadow-md'
            : 'border-[#C8D9E6] hover:border-[#567C8D] bg-[#F5F2EB]/50 hover:bg-[#F5F2EB]'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/wav,audio/mp3,audio/mpeg,audio/flac,audio/m4a,audio/ogg,audio/aac"
          className="hidden"
          onChange={handleFileInputChange}
        />

        <div className="flex flex-col items-center justify-center space-y-2.5">
          <div className="p-3 rounded-2xl bg-white border border-[#C8D9E6] text-[#567C8D] shadow-xs">
            <FileAudio className="w-7 h-7" />
          </div>
          <div>
            <p className="text-xs font-semibold text-[#2F4156]">
              Drop audio file here, or <span className="text-[#567C8D] font-bold underline underline-offset-2">browse</span>
            </p>
            <p className="text-[11px] text-[#567C8D] mt-0.5 font-mono">
              WAV, MP3, FLAC, M4A, OGG &bull; Max 15 MB
            </p>
          </div>
        </div>
      </div>

      {/* Validation Error Alert */}
      {validationError && (
        <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 flex items-center space-x-2 text-xs text-rose-800">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Selected File Preview Audio Player */}
      {selectedFile && (
        <AudioPlayerBar
          audioBlobOrFile={selectedFile}
          fileName={selectedFile.name}
          onClear={handleClear}
        />
      )}

      {/* Quick Test Bench Samples */}
      <div className="pt-2 border-t border-[#C8D9E6]/60 space-y-2">
        <div className="flex items-center justify-between text-[11px] text-[#567C8D] font-medium">
          <span>Curated Test Bench Samples:</span>
          <span className="font-mono text-[10px] text-[#567C8D]">16kHz PCM</span>
        </div>
        <div className="grid grid-cols-3 gap-2">
          <button
            type="button"
            onClick={() => handleLoadTestSample('Clean Human Phonation', 320)}
            disabled={isAnalyzing}
            className="flex items-center justify-center space-x-1.5 p-2 rounded-xl bg-[#F5F2EB] hover:bg-white border border-[#C8D9E6] hover:border-[#567C8D] text-[#2F4156] hover:text-emerald-700 text-xs font-medium transition-all disabled:opacity-50"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span className="truncate">Human Sample</span>
          </button>

          <button
            type="button"
            onClick={() => handleLoadTestSample('Replay Reverberation Artifact', 580)}
            disabled={isAnalyzing}
            className="flex items-center justify-center space-x-1.5 p-2 rounded-xl bg-[#F5F2EB] hover:bg-white border border-[#C8D9E6] hover:border-[#567C8D] text-[#2F4156] hover:text-amber-700 text-xs font-medium transition-all disabled:opacity-50"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
            <span className="truncate">Replay Echo</span>
          </button>

          <button
            type="button"
            onClick={() => handleLoadTestSample('Neural Voice Clone', 880)}
            disabled={isAnalyzing}
            className="flex items-center justify-center space-x-1.5 p-2 rounded-xl bg-[#F5F2EB] hover:bg-white border border-[#C8D9E6] hover:border-[#567C8D] text-[#2F4156] hover:text-rose-700 text-xs font-medium transition-all disabled:opacity-50"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-rose-600 shrink-0" />
            <span className="truncate">AI Voice Clone</span>
          </button>
        </div>
      </div>

      {/* Submit Action */}
      {selectedFile && (
        <div className="flex justify-end pt-1">
          <button
            onClick={handleSubmit}
            disabled={isAnalyzing}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-[#2F4156] hover:bg-[#19232f] text-white font-bold text-xs sm:text-sm shadow-sm transition-all disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            <span>{isAnalyzing ? 'Analyzing Audio...' : 'Analyze Audio File'}</span>
          </button>
        </div>
      )}
    </div>
  );
};

