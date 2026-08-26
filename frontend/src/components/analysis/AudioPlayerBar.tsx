import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, RotateCcw, Volume2, FileAudio } from 'lucide-react';
import { formatTime, formatFileSize } from '../../utils/audioUtils';

interface AudioPlayerBarProps {
  audioBlobOrFile: Blob | File | null;
  fileName?: string;
  onClear?: () => void;
  className?: string;
}

export const AudioPlayerBar: React.FC<AudioPlayerBarProps> = ({
  audioBlobOrFile,
  fileName,
  onClear,
  className = '',
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (!audioBlobOrFile) {
      setAudioUrl(null);
      setIsPlaying(false);
      setCurrentTime(0);
      setDuration(0);
      return;
    }

    const url = URL.createObjectURL(audioBlobOrFile);
    setAudioUrl(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [audioBlobOrFile]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => setIsPlaying(true)).catch((e) => console.error('Playback error', e));
    }
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    setCurrentTime(audioRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (!audioRef.current) return;
    setDuration(audioRef.current.duration || 0);
  };

  const handleEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };

  if (!audioBlobOrFile || !audioUrl) return null;

  const resolvedName = fileName || (audioBlobOrFile instanceof File ? audioBlobOrFile.name : 'Voice Sample Audio');
  const size = audioBlobOrFile.size;

  return (
    <div className={`p-3.5 rounded-2xl bg-[#F5F2EB] border border-[#C8D9E6] space-y-2.5 ${className}`}>
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
      />

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5 min-w-0">
          <div className="p-2 rounded-xl bg-white border border-[#C8D9E6] text-[#567C8D] shrink-0">
            <FileAudio className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-[#2F4156] truncate">{resolvedName}</p>
            <p className="text-[11px] text-[#567C8D] font-mono">{formatFileSize(size)}</p>
          </div>
        </div>

        {onClear && (
          <button
            onClick={onClear}
            className="text-[11px] text-[#567C8D] hover:text-rose-700 px-2 py-1 rounded hover:bg-white transition-colors"
          >
            Remove
          </button>
        )}
      </div>

      {/* Playback Controls & Progress Slider */}
      <div className="flex items-center space-x-3 pt-1">
        <button
          onClick={togglePlay}
          className="p-2 rounded-xl bg-[#2F4156] hover:bg-[#19232f] text-white shadow-xs transition-all shrink-0"
        >
          {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
        </button>

        <span className="text-[11px] font-mono text-[#567C8D] w-10 text-right font-medium">
          {formatTime(currentTime)}
        </span>

        <input
          type="range"
          min="0"
          max={duration || 100}
          step="0.05"
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-1.5 bg-[#C8D9E6] rounded-lg appearance-none cursor-pointer accent-[#567C8D]"
        />

        <span className="text-[11px] font-mono text-[#567C8D] w-10 font-medium">
          {formatTime(duration)}
        </span>
      </div>
    </div>
  );
};

