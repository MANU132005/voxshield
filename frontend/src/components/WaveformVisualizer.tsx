import React, { useEffect, useRef } from 'react';

interface WaveformVisualizerProps {
  isActive: boolean;
  color?: string;
  height?: number;
}

export const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  isActive,
  color = '#0284c7',
  height = 80
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    let phase = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const bars = 36;
      const barWidth = 3;
      const gap = (canvas.width - bars * barWidth) / (bars - 1);

      for (let i = 0; i < bars; i++) {
        let barHeight = 8;
        if (isActive) {
          const sinValue = Math.sin(phase + i * 0.2);
          const cosValue = Math.cos(phase * 1.5 + i * 0.1);
          barHeight = Math.max(8, Math.abs(sinValue * cosValue) * (canvas.height * 0.8));
        } else {
          barHeight = 6 + Math.sin(i * 0.5) * 3;
        }

        const x = i * (barWidth + gap);
        const y = (canvas.height - barHeight) / 2;

        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, '#38bdf8');
        gradient.addColorStop(1, '#0284c7');

        ctx.fillStyle = isActive ? gradient : 'rgba(51, 65, 85, 0.5)';
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, 2);
        ctx.fill();
      }

      if (isActive) {
        phase += 0.12;
      }

      animationId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [isActive, color]);

  return (
    <div className="w-full flex items-center justify-center py-2">
      <canvas
        ref={canvasRef}
        width={300}
        height={height}
        className="w-full max-w-sm rounded-lg"
      />
    </div>
  );
};
