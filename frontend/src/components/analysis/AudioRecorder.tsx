import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, RotateCcw, Send, AlertCircle, ShieldAlert, Sparkles, AudioWaveform } from 'lucide-react';
import { formatTime } from '../../utils/audioUtils';
import { WaveformLive } from './WaveformLive';
import { AudioPlayerBar } from './AudioPlayerBar';

interface AudioRecorderProps {
  onAudioReady: (blob: Blob, metadata: { name: string; sizeBytes: number; durationSeconds: number; source: 'MICROPHONE' }) => void;
  isAnalyzing: boolean;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onAudioReady,
  isAnalyzing,
}) => {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [recordingTime, setRecordingTime] = useState<number>(0);
  const [micStream, setMicStream] = useState<MediaStream | null>(null);
  const [micPermissionError, setMicPermissionError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (micStream) {
        micStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [micStream]);

  const startRecording = async () => {
    setMicPermissionError(null);
    setRecordedBlob(null);
    setRecordingTime(0);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: false, // keep ambient dynamics for realistic anti-spoofing
          autoGainControl: true,
        },
      });

      setMicStream(stream);

      // Prefer standard audio formats supported by browser
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/ogg')
        ? 'audio/ogg'
        : 'audio/wav';

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        setRecordedBlob(audioBlob);
        // Stop audio tracks after recording finishes
        stream.getTracks().forEach((track) => track.stop());
        setMicStream(null);
      };

      mediaRecorder.start(250); // Slice every 250ms
      setIsRecording(true);

      timerIntervalRef.current = window.setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      console.error('Microphone access failure', err);
      setMicPermissionError(
        err.name === 'NotAllowedError'
          ? 'Microphone permission was denied by browser. Please allow microphone access in your browser settings to record live voice audio.'
          : 'Could not access microphone hardware. You can also upload pre-recorded audio files.'
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

  const handleCancel = () => {
    if (isRecording && mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    if (micStream) {
      micStream.getTracks().forEach((track) => track.stop());
      setMicStream(null);
    }
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    setIsRecording(false);
    setRecordedBlob(null);
    setRecordingTime(0);
    audioChunksRef.current = [];
  };

  const handleSendForAnalysis = () => {
    if (!recordedBlob) return;
    onAudioReady(recordedBlob, {
      name: `live_mic_capture_${Date.now()}.wav`,
      sizeBytes: recordedBlob.size,
      durationSeconds: recordingTime,
      source: 'MICROPHONE',
    });
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm flex flex-col justify-between space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-[#C8D9E6]/40 border border-[#C8D9E6] text-[#2F4156]">
            <Mic className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-[#2F4156] text-sm sm:text-base">Live Microphone Capture</h3>
            <p className="text-[11px] text-[#567C8D]">Sample voice phonation for instant anti-spoofing audit</p>
          </div>
        </div>

        {isRecording && (
          <span className="flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-50 border border-rose-300 text-rose-700 text-xs font-mono font-bold animate-pulse shadow-xs">
            <span className="w-2 h-2 rounded-full bg-rose-600 animate-ping"></span>
            <span>REC {formatTime(recordingTime)}</span>
          </span>
        )}
      </div>

      {/* Live Frequency Visualizer */}
      <WaveformLive isRecording={isRecording} stream={micStream} height={90} />

      {/* Microphone Permission / Device Error */}
      {micPermissionError && (
        <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 flex items-start space-x-2 text-xs text-rose-800">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 mt-0.5" />
          <span>{micPermissionError}</span>
        </div>
      )}

      {/* Recorded Sample Audio Preview Player */}
      {recordedBlob && !isRecording && (
        <AudioPlayerBar
          audioBlobOrFile={recordedBlob}
          fileName={`Recorded Voice Sample (${formatTime(recordingTime)})`}
          onClear={handleCancel}
        />
      )}

      {/* Action Controls */}
      <div className="flex items-center justify-center space-x-3 pt-2">
        {!isRecording && !recordedBlob && (
          <button
            onClick={startRecording}
            disabled={isAnalyzing}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-[#2F4156] hover:bg-[#19232f] text-white font-semibold text-xs sm:text-sm shadow-sm transition-all duration-200 disabled:opacity-50"
          >
            <Mic className="w-4 h-4" />
            <span>Record Voice Sample</span>
          </button>
        )}

        {isRecording && (
          <div className="flex items-center space-x-3">
            <button
              onClick={handleCancel}
              className="px-4 py-2.5 rounded-xl bg-[#F5F2EB] hover:bg-white text-[#2F4156] border border-[#C8D9E6] font-medium text-xs transition-all"
            >
              Cancel
            </button>
            <button
              onClick={stopRecording}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs sm:text-sm shadow-md transition-all animate-pulse"
            >
              <Square className="w-4 h-4" />
              <span>Stop Recording</span>
            </button>
          </div>
        )}

        {recordedBlob && !isRecording && (
          <div className="flex items-center space-x-3 w-full justify-end">
            <button
              onClick={handleCancel}
              disabled={isAnalyzing}
              className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl bg-[#F5F2EB] hover:bg-white text-[#2F4156] border border-[#C8D9E6] text-xs font-medium transition-all"
              title="Discard & Record Again"
            >
              <RotateCcw className="w-3.5 h-3.5 text-[#567C8D]" />
              <span>Record Again</span>
            </button>
            <button
              onClick={handleSendForAnalysis}
              disabled={isAnalyzing}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-[#567C8D] hover:bg-[#476878] text-white font-bold text-xs sm:text-sm shadow-sm transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              <span>{isAnalyzing ? 'Submitting...' : 'Analyze Voice'}</span>
            </button>
          </div>
        )}
      </div>

      {/* Privacy note */}
      <div className="text-center">
        <span className="text-[10px] text-[#567C8D] font-mono font-medium">
          Audio is captured into client memory and securely transmitted via HTTPS.
        </span>
      </div>
    </div>
  );
};

