import React from 'react';
import { Shield, Lock, Cpu, HeartHandshake } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-[#C8D9E6] bg-white py-8 px-4 lg:px-8 text-xs text-[#567C8D] mt-16 shadow-sm">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Top Tier: Philosophy & Principles */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 border-b border-[#C8D9E6]/60 pb-6 text-center md:text-left">
          <div className="space-y-1">
            <div className="flex items-center justify-center md:justify-start space-x-2 text-[#2F4156] font-bold text-sm">
              <Shield className="w-4 h-4 text-[#567C8D]" />
              <span>VOXSHIELD CORE PHILOSOPHY</span>
            </div>
            <p className="text-[11px] text-[#567C8D] font-mono tracking-wider font-semibold">
              DETECT &rarr; VERIFY &rarr; SCORE &rarr; EXPLAIN &rarr; PREVENT
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 text-[11px] font-mono">
            <span className="px-2.5 py-1 rounded-lg bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] font-medium">
              ClaimGuard Enabled
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] font-medium">
              Zero Raw Audio Retention
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-[#F5F2EB] border border-[#C8D9E6] text-[#2F4156] font-medium">
              Scientific Boundaries Certified
            </span>
          </div>
        </div>

        {/* Bottom Tier: Credits & SIH Project info */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px]">
          <p className="text-[#2F4156] font-medium">
            &copy; 2026 VoxShield AI &bull; SIH26104 Voice Impersonation & Deepfake Defense System
          </p>
          <div className="flex items-center space-x-4 text-[#567C8D]">
            <span className="font-mono">FastAPI REST Gateway (v1.0.0)</span>
            <span>&bull;</span>
            <span className="font-mono">React SOC Engine</span>
          </div>
        </div>

      </div>
    </footer>
  );
};

