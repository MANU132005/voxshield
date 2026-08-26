import React from 'react';
import { History, Eye, Clock, FileAudio, Shield, Hash, ArrowUpRight, Inbox } from 'lucide-react';
import { SessionAuditRecord } from '../../api/types';
import { Badge } from '../common/Badge';
import { EmptyState } from '../common/EmptyState';
import { formatFileSize, formatTime } from '../../utils/audioUtils';

interface SessionAuditTableProps {
  records: SessionAuditRecord[];
  onSelectRecord: (record: SessionAuditRecord) => void;
  onClearSession?: () => void;
}

export const SessionAuditTable: React.FC<SessionAuditTableProps> = ({
  records,
  onSelectRecord,
  onClearSession,
}) => {
  return (
    <div className="bg-white rounded-2xl p-6 border border-[#C8D9E6] shadow-sm space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#C8D9E6]/60 pb-4">
        <div className="flex items-center space-x-2.5">
          <History className="w-5 h-5 text-[#567C8D]" />
          <div>
            <h3 className="font-bold text-[#2F4156] text-base">Session Investigation Log</h3>
            <p className="text-xs text-[#567C8D]">
              Ephemeral in-memory session audit records ({records.length})
            </p>
          </div>
        </div>

        {records.length > 0 && onClearSession && (
          <button
            onClick={onClearSession}
            className="text-xs text-[#567C8D] hover:text-rose-700 px-3 py-1.5 rounded-lg hover:bg-[#F5F2EB] border border-transparent hover:border-[#C8D9E6] transition-all font-medium"
          >
            Clear Session History
          </button>
        )}
      </div>

      {records.length === 0 ? (
        <EmptyState
          title="No Persistent Analysis History Available"
          description="VoxShield enforces zero raw audio and metadata persistence on the backend by default. Session audits appear here during active console usage."
          icon={Inbox}
          badgeText="ZERO PERSISTENCE PROTOCOL"
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#C8D9E6] text-[#567C8D] font-mono text-[11px] uppercase tracking-wider">
                <th className="py-3 px-3">Audit ID / Time</th>
                <th className="py-3 px-3">Sample Payload</th>
                <th className="py-3 px-3">Decision</th>
                <th className="py-3 px-3">Threat Index</th>
                <th className="py-3 px-3">AI / Replay</th>
                <th className="py-3 px-3">Latency</th>
                <th className="py-3 px-3 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#C8D9E6]/40">
              {records.map((rec) => (
                <tr
                  key={rec.id}
                  onClick={() => onSelectRecord(rec)}
                  className="hover:bg-[#F5F2EB]/70 cursor-pointer transition-colors group"
                >
                  {/* Audit ID & Time */}
                  <td className="py-3.5 px-3">
                    <p className="font-mono text-[#2F4156] text-xs font-bold group-hover:underline">
                      {rec.requestId}
                    </p>
                    <span className="text-[10px] text-[#567C8D] font-mono font-medium">
                      {new Date(rec.timestamp).toLocaleTimeString()}
                    </span>
                  </td>

                  {/* Sample Payload */}
                  <td className="py-3.5 px-3">
                    <div className="flex items-center space-x-2">
                      <FileAudio className="w-4 h-4 text-[#567C8D] shrink-0" />
                      <div className="min-w-0">
                        <p className="text-[#2F4156] font-semibold truncate max-w-[140px] sm:max-w-[180px]">
                          {rec.filename}
                        </p>
                        <p className="text-[10px] text-[#567C8D] font-mono">
                          {formatFileSize(rec.fileSizeBytes)}
                          {rec.durationSeconds ? ` • ${formatTime(rec.durationSeconds)}` : ''}
                        </p>
                      </div>
                    </div>
                  </td>

                  {/* Decision */}
                  <td className="py-3.5 px-3">
                    <Badge variant={rec.decision} size="sm" />
                  </td>

                  {/* Threat Index */}
                  <td className="py-3.5 px-3 font-mono font-bold">
                    <span
                      className={
                        rec.riskScore >= 0.70
                          ? 'text-rose-700'
                          : rec.riskScore >= 0.35
                          ? 'text-amber-700'
                          : 'text-emerald-700'
                      }
                    >
                      {Math.round(rec.riskScore * 100)}% ({rec.riskScore})
                    </span>
                  </td>

                  {/* AI / Replay decomposition */}
                  <td className="py-3.5 px-3 font-mono text-[11px] text-[#2F4156]">
                    <div>AI: <strong className="text-[#2F4156] font-bold">{Math.round(rec.syntheticScore * 100)}%</strong></div>
                    <div>DSP: <strong className="text-[#2F4156] font-bold">{Math.round(rec.replayScore * 100)}%</strong></div>
                  </td>

                  {/* Latency */}
                  <td className="py-3.5 px-3 font-mono text-[11px] text-[#567C8D] font-medium">
                    {rec.latencyMs}ms
                  </td>

                  {/* Inspect Button */}
                  <td className="py-3.5 px-3 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectRecord(rec);
                      }}
                      className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-[#F5F2EB] group-hover:bg-[#567C8D] group-hover:text-white border border-[#C8D9E6] text-[#2F4156] text-xs transition-all font-medium"
                    >
                      <span>View</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

