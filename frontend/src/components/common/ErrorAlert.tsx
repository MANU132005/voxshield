import React, { useEffect, useState } from 'react';
import { AlertOctagon, RotateCcw, WifiOff, ShieldAlert, Clock, X } from 'lucide-react';
import { ApiError } from '../../api/types';
import { RequestIdCopy } from './RequestIdCopy';

interface ErrorAlertProps {
  error: ApiError | string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, onRetry, onDismiss }) => {
  const isObj = typeof error === 'object';
  const message = isObj ? error.message : error;
  const statusCode = isObj ? error.statusCode : undefined;
  const requestId = isObj ? error.requestId : undefined;
  const isNetwork = isObj ? error.isNetworkError : false;
  const retryAfter = isObj ? error.retryAfterSeconds : undefined;

  const [countdown, setCountdown] = useState<number | undefined>(retryAfter);

  useEffect(() => {
    if (!retryAfter || retryAfter <= 0) return;
    setCountdown(retryAfter);

    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (!prev || prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [retryAfter]);

  return (
    <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 shadow-sm space-y-3 animate-in fade-in duration-300">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div className="p-2 rounded-xl bg-rose-100 border border-rose-300 text-rose-700 shrink-0 mt-0.5">
            {isNetwork ? <WifiOff className="w-5 h-5" /> : <AlertOctagon className="w-5 h-5" />}
          </div>
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <h4 className="font-bold text-rose-950 text-sm">
                {isNetwork
                  ? 'Backend Service Unreachable'
                  : statusCode === 413
                  ? 'Payload Limit Exceeded (413)'
                  : statusCode === 429
                  ? 'Rate Limit Exceeded (429)'
                  : statusCode === 400
                  ? 'Invalid Audio Payload (400)'
                  : 'Audio Security Analysis Failed'}
              </h4>
              {statusCode && (
                <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-mono text-[10px] font-bold border border-rose-200">
                  HTTP {statusCode}
                </span>
              )}
            </div>
            <p className="text-xs text-rose-800 leading-relaxed">{message}</p>
          </div>
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="p-1 rounded-lg text-rose-500 hover:text-rose-900 hover:bg-rose-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {(requestId || onRetry || (countdown !== undefined && countdown > 0)) && (
        <div className="pt-2 border-t border-rose-200 flex flex-wrap items-center justify-between gap-2 text-xs">
          {requestId ? (
            <div className="flex items-center space-x-2">
              <span className="text-rose-700 text-[11px] font-medium">Audit ID:</span>
              <RequestIdCopy requestId={requestId} className="bg-white border-rose-200 text-rose-900" />
            </div>
          ) : (
            <div />
          )}

          <div className="flex items-center space-x-2">
            {countdown !== undefined && countdown > 0 && (
              <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-rose-100 text-rose-800 border border-rose-200 font-mono text-[11px] font-semibold">
                <Clock className="w-3 h-3 text-rose-600" />
                <span>Retry in {countdown}s</span>
              </span>
            )}

            {onRetry && (
              <button
                onClick={onRetry}
                disabled={countdown !== undefined && countdown > 0}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-rose-700 hover:bg-rose-800 text-white font-medium text-xs border border-rose-800 transition-all shadow-xs disabled:opacity-40"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Retry Analysis</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

