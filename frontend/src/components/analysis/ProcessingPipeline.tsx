import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, Cpu, Radio, Shield, AudioWaveform, Activity, Binary, Layers } from 'lucide-react';

export const ProcessingPipeline: React.FC = () => {
  const [activeStep, setActiveStep] = useState<number>(0);

  const steps = [
    { title: 'Audio Ingestion & Normalization', desc: 'Decoding stream & standardizing to 16kHz mono PCM', icon: AudioWaveform },
    { title: 'Spectral Feature Extraction', desc: 'Computing LFCC cepstral coefficients & STFT spectrogram', icon: Layers },
    { title: 'Deep Neural Anti-Spoofing Classifier', desc: 'Evaluating voice cloning and vocoder phase anomalies', icon: Cpu },
    { title: 'Acoustic Replay DSP Engine', desc: 'Analyzing room impulse response (RIR) and transducer noise', icon: Radio },
    { title: 'Contextual Risk Engine Aggregation', desc: 'Synthesizing weighted threat vectors into decision matrix', icon: Shield },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 450);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#C8D9E6] space-y-6 shadow-md">
      
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-[#C8D9E6]/60 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-2xl bg-[#C8D9E6]/40 border border-[#C8D9E6] text-[#2F4156]">
            <Loader2 className="w-6 h-6 animate-spin text-[#567C8D]" />
          </div>
          <div>
            <h3 className="font-extrabold text-base sm:text-lg text-[#2F4156] tracking-tight">
              Executing Voice Security Inference Pipeline
            </h3>
            <p className="text-xs text-[#567C8D] font-mono mt-0.5 font-medium">
              POST /api/v1/analyze &bull; FastAPI Multi-Stage Classifier
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] font-mono text-xs font-semibold animate-pulse">
          <Activity className="w-3.5 h-3.5 text-[#567C8D]" />
          <span>INFERENCE ACTIVE</span>
        </div>
      </div>

      {/* Pipeline Stages Vertical Stepper */}
      <div className="space-y-3">
        {steps.map((step, idx) => {
          const isDone = idx < activeStep;
          const isCurrent = idx === activeStep;
          const isPending = idx > activeStep;
          const Icon = step.icon;

          return (
            <div
              key={idx}
              className={`flex items-center space-x-4 p-3.5 rounded-2xl border transition-all duration-300 ${
                isCurrent
                  ? 'bg-[#F5F2EB] border-[#567C8D] shadow-xs scale-[1.01]'
                  : isDone
                  ? 'bg-[#F5F2EB]/50 border-[#C8D9E6] text-[#2F4156]'
                  : 'bg-white border-[#C8D9E6]/50 opacity-40'
              }`}
            >
              <div
                className={`p-2 rounded-xl border shrink-0 transition-all ${
                  isDone
                    ? 'bg-emerald-50 border-emerald-300 text-emerald-700'
                    : isCurrent
                    ? 'bg-[#567C8D] border-[#2F4156] text-white animate-pulse'
                    : 'bg-[#F5F2EB] border-[#C8D9E6] text-[#567C8D]'
                }`}
              >
                {isDone ? <CheckCircle2 className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className={`text-xs font-bold ${isCurrent ? 'text-[#2F4156]' : isDone ? 'text-[#2F4156]' : 'text-[#567C8D]'}`}>
                    {step.title}
                  </h4>
                  <span className="text-[10px] font-mono text-[#567C8D] font-medium">
                    {isDone ? 'COMPLETED' : isCurrent ? 'RUNNING...' : 'QUEUED'}
                  </span>
                </div>
                <p className="text-[11px] text-[#567C8D] truncate mt-0.5">{step.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};

