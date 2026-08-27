import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Play, RotateCcw, Send, AlertCircle } from 'lucide-react';
import { formatTime } from '../utils/audioUtils';
import { WaveformVisualizer } from './WaveformVisualizer';

interface AudioRecorderProps {
  onAudioReady: (blob: Blob) => void;
  isAnalyzing: boolean;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onAudioReady,
  isAnalyzing,
}) => {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [recordingTime, setRecordingTime] = useState<number>(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [micPermissionError, setMicPermissionError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  const startRecording = async () => {
    setMicPermissionError(null);
    setRecordedBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : MediaRecorder.isTypeSupported('audio/mp4')
        ? 'audio/mp4'
        : '';

      const mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

const encodeWav = (samples: Float32Array, sampleRate: number): Blob => {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  const writeString = (offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  writeString(0, 'RIFF');
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(8, 'WAVE');
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(36, 'data');
  view.setUint32(40, samples.length * 2, true);

  let offset = 44;
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }

  return new Blob([buffer], { type: 'audio/wav' });
};

      mediaRecorder.onstop = async () => {
        const actualMime = mediaRecorder.mimeType || 'audio/webm';
        const rawBlob = new Blob(audioChunksRef.current, { type: actualMime });
        
        try {
          const arrayBuffer = await rawBlob.arrayBuffer();
          const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
          const decodedAudio = await audioCtx.decodeAudioData(arrayBuffer);
          const channelData = decodedAudio.getChannelData(0);
          const wavBlob = encodeWav(channelData, decodedAudio.sampleRate);
          const micFile = new File([wavBlob], 'mic_recording.wav', { type: 'audio/wav' });
          setRecordedBlob(micFile);
          const url = URL.createObjectURL(wavBlob);
          setAudioUrl(url);
          audioCtx.close();
        } catch (convErr) {
          const ext = actualMime.includes('mp4') ? 'm4a' : actualMime.includes('webm') ? 'webm' : 'wav';
          const micFile = new File([rawBlob], `mic_recording.${ext}`, { type: actualMime });
          setRecordedBlob(micFile);
          const url = URL.createObjectURL(rawBlob);
          setAudioUrl(url);
        }

        // Stop all audio tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);

      timerIntervalRef.current = window.setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);

    } catch (err: any) {
      setMicPermissionError(
        'Microphone access denied or unavailable. You can also upload sample audio files.'
      );
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = null;
      }
    }
  };

  const handleSendForAnalysis = () => {
    if (recordedBlob) {
      onAudioReady(recordedBlob);
    }
  };

  const handleReset = () => {
    setRecordedBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
  };

  return (
    <div className="bg-slate-900/60 rounded-2xl p-6 border border-slate-800 flex flex-col justify-between h-full">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Mic className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-sm">Microphone Recorder</h3>
            <p className="text-xs text-slate-400">
              {isRecording
                ? 'Listening for voice sample...'
                : recordedBlob
                ? 'Recording captured ✓'
                : 'Click record to capture voice'}
            </p>
          </div>
        </div>
        {isRecording && (
          <span className="flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-950 border border-rose-500/40 text-rose-400 text-xs font-mono font-bold animate-pulse">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
            <span>● RECORDING {formatTime(recordingTime)}</span>
          </span>
        )}
      </div>

      {/* Waveform Visualization Canvas */}
      <WaveformVisualizer isActive={isRecording} />

      {/* Error Alert */}
      {micPermissionError && (
        <div className="mb-4 p-3 rounded-xl bg-amber-950/40 border border-amber-500/30 flex items-center space-x-2 text-xs text-amber-300">
          <AlertCircle className="w-4 h-4 shrink-0 text-amber-400" />
          <span>{micPermissionError}</span>
        </div>
      )}

      {/* Audio Playback Preview if recorded */}
      {audioUrl && !isRecording && (
        <div className="mb-4 p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-slate-300">
            <Play className="w-4 h-4 text-cyan-400" />
            <span>Recorded Voice Sample ({formatTime(recordingTime)})</span>
          </div>
          <audio src={audioUrl} controls className="h-7 w-48 text-xs" />
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-center space-x-3 pt-2">
        {!isRecording && !recordedBlob && (
          <button
            onClick={startRecording}
            disabled={isAnalyzing}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition-all disabled:opacity-50"
          >
            <Mic className="w-4 h-4" />
            <span>START RECORDING</span>
          </button>
        )}

        {isRecording && (
          <button
            onClick={stopRecording}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition-all"
          >
            <Square className="w-4 h-4" />
            <span>STOP RECORDING</span>
          </button>
        )}

        {recordedBlob && !isRecording && (
          <>
            <button
              onClick={handleReset}
              disabled={isAnalyzing}
              className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all text-xs"
              title="Record Again"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={handleSendForAnalysis}
              disabled={isAnalyzing}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs uppercase tracking-wider transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              <span>{isAnalyzing ? 'ANALYZING...' : 'ANALYZE AUDIO'}</span>
            </button>
          </>
        )}
      </div>
    </div>
  );
};
