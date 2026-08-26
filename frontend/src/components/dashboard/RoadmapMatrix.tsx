import React from 'react';
import { Layers, CheckCircle2, Clock, ShieldCheck, Sparkles, Cpu, Radio, UserCheck, MessageSquare, PhoneForwarded } from 'lucide-react';

export const RoadmapMatrix: React.FC = () => {
  const currentCapabilities = [
    { name: 'Audio File Upload Analysis', desc: 'Accepts WAV, MP3, FLAC, M4A, OGG up to 15MB' },
    { name: 'Live Web Audio Recording', desc: 'Browser mic capture with real-time frequency spectrum' },
    { name: 'Deep Neural Anti-Spoofing', desc: 'Predicts P(synthetic) from LFCC & spectral phase anomalies' },
    { name: 'Acoustic Replay DSP Engine', desc: 'Detects room reverberation & physical transducer noise' },
    { name: 'Contextual Risk Engine', desc: 'Aggregated weighted threat scoring & security decisions' },
    { name: 'Diagnostic Evidence & Counter-Evidence', desc: 'Dual-directional finding verification with ClaimGuard' },
    { name: 'Attack Vector Hypotheses', desc: 'Contextual qualitative threat classification' },
    { name: '10-Stage Forensic Processing Timeline', desc: 'Detailed stage latency and audit telemetry trail' },
  ];

  const futureCapabilities = [
    { phase: 'PHASE 2', name: 'Real-Time WebSocket Audio Streaming', desc: 'Frame-by-frame live chunk inference (/api/v1/stream)', icon: Radio },
    { phase: 'PHASE 2', name: 'Biometric Speaker Verification', desc: 'Voice print enrollment & 1:1 speaker identity matching', icon: UserCheck },
    { phase: 'PHASE 3', name: 'Dynamic Voice Liveness Challenge', desc: 'Randomized phonetic prompt challenge-response protocol', icon: MessageSquare },
    { phase: 'PHASE 4', name: 'Telephony & SIP / Twilio Integration', desc: 'Real-time call center voice security gateway interceptor', icon: PhoneForwarded },
    { phase: 'PHASE 5', name: 'Cloud Multi-Tenant Audit Persistence', desc: 'Encrypted long-term SOC audit database with compliance exports', icon: Layers },
  ];

  return (
    <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-2.5 border-b border-[#C8D9E6]/60 pb-4">
        <Layers className="w-5 h-5 text-[#567C8D]" />
        <div>
          <h3 className="font-bold text-[#2F4156] text-base">System Capabilities & Phased Roadmap</h3>
          <p className="text-xs text-[#567C8D]">Current Production Feature Set vs Future Enterprise Integrations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Current Active Features */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2 text-xs font-bold text-emerald-700 uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Currently Active & Operational (Phase 1)</span>
          </div>

          <div className="space-y-2">
            {currentCapabilities.map((cap, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-[#F5F2EB] border border-[#C8D9E6] flex items-start space-x-3"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 shrink-0" />
                <div className="min-w-0">
                  <h4 className="font-bold text-xs text-[#2F4156]">{cap.name}</h4>
                  <p className="text-[11px] text-[#567C8D] leading-relaxed">{cap.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Future Roadmap */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2 text-xs font-bold text-[#567C8D] uppercase tracking-wider">
            <Clock className="w-4 h-4 text-[#567C8D]" />
            <span>Future Roadmap (Phase 2 - 5+)</span>
          </div>

          <div className="space-y-2">
            {futureCapabilities.map((cap, idx) => {
              const Icon = cap.icon;
              return (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-[#F5F2EB]/60 border border-[#C8D9E6]/80 flex items-start space-x-3"
                >
                  <div className="p-1.5 rounded-lg bg-[#C8D9E6]/50 border border-[#C8D9E6] text-[#2F4156] shrink-0 mt-0.5">
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-xs text-[#2F4156]">{cap.name}</h4>
                      <span className="px-2 py-0.5 rounded bg-[#C8D9E6]/60 text-[#2F4156] border border-[#C8D9E6] text-[9px] font-mono font-bold">
                        {cap.phase}
                      </span>
                    </div>
                    <p className="text-[11px] text-[#567C8D] leading-relaxed mt-0.5">{cap.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
};

