import React from 'react';
import { Cpu, Radio, UserCheck, CheckCircle2, AlertTriangle, ShieldAlert, Sparkles, HelpCircle } from 'lucide-react';
import { BackendAnalysisResponse } from '../../api/types';

interface SignalGridProps {
  response: BackendAnalysisResponse;
}

export const SignalGrid: React.FC<SignalGridProps> = ({ response }) => {
  const synthPercent = Math.round(response.synthetic_score * 100);
  const replayPercent = Math.round(response.replay_score * 100);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      
      {/* 1. AI Anti-Spoofing Neural Classifier Card */}
      <div className="bg-white rounded-2xl p-5 border border-[#C8D9E6] shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-[#C8D9E6]/40 border border-[#C8D9E6] text-[#2F4156]">
              <Cpu className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold text-[#2F4156]">AI Anti-Spoofing</span>
          </div>
          <span className="font-mono text-xs font-bold text-[#2F4156]">
            {synthPercent}% ({response.synthetic_score})
          </span>
        </div>

        {/* Progress Bar */}
        <div className="space-y-1">
          <div className="h-2 w-full bg-[#C8D9E6] rounded-full overflow-hidden p-0.5">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                response.synthetic_score >= 0.70
                  ? 'bg-rose-600'
                  : response.synthetic_score >= 0.40
                  ? 'bg-amber-500'
                  : 'bg-emerald-600'
              }`}
              style={{ width: `${synthPercent}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] font-mono text-[#567C8D] font-medium">
            <span>Natural Voice</span>
            <span>Cloned / TTS</span>
          </div>
        </div>

        <p className="text-[11px] text-[#567C8D] leading-relaxed">
          {response.synthetic_score >= 0.70
            ? 'Strong artificial vocoder markers & phase discontinuities detected.'
            : response.synthetic_score >= 0.40
            ? 'Minor acoustic synthesis anomalies observed in higher frequency bands.'
            : 'Natural human vocal tract formants and harmonic ratios verified.'}
        </p>
      </div>

      {/* 2. Acoustic Replay & DSP Spectral Card */}
      <div className="bg-white rounded-2xl p-5 border border-[#C8D9E6] shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-[#C8D9E6]/40 border border-[#C8D9E6] text-[#2F4156]">
              <Radio className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold text-[#2F4156]">Replay & DSP Analysis</span>
          </div>
          <span className="font-mono text-xs font-bold text-[#2F4156]">
            {replayPercent}% ({response.replay_score})
          </span>
        </div>

        {/* Progress Bar */}
        <div className="space-y-1">
          <div className="h-2 w-full bg-[#C8D9E6] rounded-full overflow-hidden p-0.5">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                response.replay_score >= 0.65
                  ? 'bg-rose-600'
                  : response.replay_score >= 0.40
                  ? 'bg-amber-500'
                  : 'bg-emerald-600'
              }`}
              style={{ width: `${replayPercent}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] font-mono text-[#567C8D] font-medium">
            <span>Direct Path</span>
            <span>Speaker Playback</span>
          </div>
        </div>

        <p className="text-[11px] text-[#567C8D] leading-relaxed">
          {response.replay_score >= 0.65
            ? 'Secondary room reverberation & loudspeaker transducer noise detected.'
            : response.replay_score >= 0.40
            ? 'Slight room echo anomalies detected; verify acoustic capture environment.'
            : 'Clean direct-path acoustic impulse response without secondary playback.'}
        </p>
      </div>

      {/* 3. Biometric Speaker Verification (Honest null status) */}
      <div className="bg-white rounded-2xl p-5 border border-[#C8D9E6] shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] text-[#567C8D]">
              <UserCheck className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold text-[#2F4156]">Biometric Verification</span>
          </div>
          <span className="px-2 py-0.5 rounded bg-[#F5F2EB] border border-[#C8D9E6] text-[#567C8D] font-mono text-[10px] font-bold">
            {response.speaker_match === null ? 'null' : `${response.speaker_match}%`}
          </span>
        </div>

        {/* Progress Bar (Disabled/Phase 2) */}
        <div className="space-y-1">
          <div className="h-2 w-full bg-[#C8D9E6]/60 rounded-full overflow-hidden">
            <div className="h-full bg-[#567C8D]/40 w-0" />
          </div>
          <div className="flex justify-between text-[10px] font-mono text-[#567C8D] font-medium">
            <span>Un-enrolled</span>
            <span>Phase 2 Roadmap</span>
          </div>
        </div>

        <p className="text-[11px] text-[#567C8D] leading-relaxed">
          Speaker identity matching is not active for this analysis. Anti-spoofing focuses on synthetic voice & replay verification.
        </p>
      </div>

    </div>
  );
};

