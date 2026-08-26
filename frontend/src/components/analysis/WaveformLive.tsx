import React, { useEffect, useRef } from 'react';

interface WaveformLiveProps {
  isRecording: boolean;
  stream: MediaStream | null;
  height?: number;
}

export const WaveformLive: React.FC<WaveformLiveProps> = ({
  isRecording,
  stream,
  height = 90,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (isRecording && stream) {
      try {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        const audioCtx = new AudioContextClass();
        audioContextRef.current = audioCtx;

        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 128;
        analyser.smoothingTimeConstant = 0.8;
        analyserRef.current = analyser;

        const source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyser);
        sourceRef.current = source;

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
          animationFrameRef.current = requestAnimationFrame(draw);
          analyser.getByteFrequencyData(dataArray);

          ctx.clearRect(0, 0, canvas.width, canvas.height);

          // Draw subtle background grid lines in Sky Blue
          ctx.strokeStyle = 'rgba(200, 217, 230, 0.5)';
          ctx.lineWidth = 1;
          for (let y = 10; y < canvas.height; y += 20) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
          }

          const barCount = 36;
          const barWidth = 4;
          const totalBarsWidth = barCount * barWidth;
          const gap = (canvas.width - totalBarsWidth) / (barCount - 1);

          for (let i = 0; i < barCount; i++) {
            const dataIndex = Math.floor((i / barCount) * bufferLength);
            const value = dataArray[dataIndex] || 0;
            const percent = value / 255;
            const barHeight = Math.max(6, percent * (canvas.height - 14));

            const x = i * (barWidth + gap);
            const y = (canvas.height - barHeight) / 2;

            // Frequency gradient: Navy and Teal with Rose peak if > 0.75
            const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
            if (percent > 0.75) {
              gradient.addColorStop(0, '#e11d48'); // Rose peak
              gradient.addColorStop(1, '#567C8D'); // Teal base
            } else {
              gradient.addColorStop(0, '#567C8D'); // Teal
              gradient.addColorStop(1, '#2F4156'); // Navy
            }

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.roundRect(x, y, barWidth, barHeight, 2);
            ctx.fill();
          }
        };

        draw();
      } catch (err) {
        console.error('Error initializing Web Audio API analyser', err);
      }
    } else {
      // Idle state renderer
      let phase = 0;
      const renderIdle = () => {
        animationFrameRef.current = requestAnimationFrame(renderIdle);
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw quiescent baseline grid
        ctx.strokeStyle = 'rgba(200, 217, 230, 0.4)';
        ctx.lineWidth = 1;
        for (let y = 15; y < canvas.height; y += 20) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(canvas.width, y);
          ctx.stroke();
        }

        const barCount = 36;
        const barWidth = 4;
        const totalBarsWidth = barCount * barWidth;
        const gap = (canvas.width - totalBarsWidth) / (barCount - 1);

        for (let i = 0; i < barCount; i++) {
          const barHeight = 4 + Math.sin(phase + i * 0.3) * 2;
          const x = i * (barWidth + gap);
          const y = (canvas.height - barHeight) / 2;

          ctx.fillStyle = 'rgba(86, 124, 141, 0.3)';
          ctx.beginPath();
          ctx.roundRect(x, y, barWidth, barHeight, 2);
          ctx.fill();
        }
        phase += 0.03;
      };

      renderIdle();
    }

    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      if (sourceRef.current) sourceRef.current.disconnect();
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(() => {});
      }
    };
  }, [isRecording, stream]);

  return (
    <div className="w-full bg-[#F5F2EB] rounded-xl p-3 border border-[#C8D9E6] flex items-center justify-center shadow-inner relative overflow-hidden">
      <canvas
        ref={canvasRef}
        width={360}
        height={height}
        className="w-full max-w-md h-full rounded"
      />
      {isRecording && (
        <div className="absolute top-2 right-3 flex items-center space-x-1.5 px-2 py-0.5 rounded bg-rose-50 border border-rose-300 text-[10px] font-mono font-bold text-rose-700">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-600 animate-ping" />
          <span>LIVE SPECTRUM</span>
        </div>
      )}
    </div>
  );
};

