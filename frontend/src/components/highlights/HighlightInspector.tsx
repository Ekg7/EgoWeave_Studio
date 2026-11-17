import React from 'react';
import { HighlightSegment } from '../../types';
import { Sparkles, CheckCircle2, AlertTriangle, Play, Flame } from 'lucide-react';

interface HighlightInspectorProps {
  highlights: HighlightSegment[];
  durationSec: number;
  currentTime: number;
  onSeek: (time: number) => void;
  isHighlightMode: boolean;
  onToggleHighlightMode: () => void;
}

export const HighlightInspector: React.FC<HighlightInspectorProps> = ({
  highlights,
  durationSec,
  currentTime,
  onSeek,
  isHighlightMode,
  onToggleHighlightMode,
}) => {
  const totalHighlightSec = highlights.reduce(
    (acc, h) => acc + (h.segment[1] - h.segment[0]),
    0
  );

  const budgetPct = durationSec > 0 ? (totalHighlightSec / durationSec) * 100 : 0;
  const isBudgetCompliant = budgetPct <= 15.0;
  const hasSegmentGe4s = highlights.some(
    (h) => h.segment[1] - h.segment[0] >= 4.0
  );

  return (
    <div className="flex flex-col h-full bg-surface-50 border border-border rounded-xl overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b border-border bg-[#0b0f19] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-4 w-4 text-cyan-400" />
          <span className="text-xs font-semibold text-slate-200">Highlight Segments</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-200 text-slate-400">
            {highlights.length} intervals
          </span>
        </div>

        {/* Highlight Mode Toggle */}
        <button
          onClick={onToggleHighlightMode}
          className={`flex items-center space-x-1 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
            isHighlightMode
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
              : 'bg-surface-100 text-slate-300 hover:bg-surface-200 border border-border'
          }`}
        >
          <Flame className="h-3.5 w-3.5 text-cyan-400" />
          <span>{isHighlightMode ? 'Viewing Highlight Stream' : 'Switch to Highlight'}</span>
        </button>
      </div>

      {/* Budget Metric Banner */}
      <div className="p-3 bg-surface-100 border-b border-border space-y-2">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-400">Duration Budget:</span>
            <span className="font-mono font-semibold text-slate-200">
              {totalHighlightSec.toFixed(1)}s / {(0.15 * durationSec).toFixed(1)}s
            </span>
            <span className="font-mono text-cyan-400 font-bold">
              ({budgetPct.toFixed(1)}%)
            </span>
          </div>

          <div className="flex items-center space-x-1 text-[11px]">
            {isBudgetCompliant ? (
              <span className="flex items-center text-emerald-400 font-medium">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Budget Compliant (&le; 15%)
              </span>
            ) : (
              <span className="flex items-center text-rose-400 font-medium">
                <AlertTriangle className="h-3 w-3 mr-1" />
                Exceeds 15% Budget
              </span>
            )}
          </div>
        </div>

        {/* Progress bar for 15% budget */}
        <div className="relative w-full h-2 bg-surface-300 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              isBudgetCompliant ? 'bg-cyan-400' : 'bg-rose-500'
            }`}
            style={{ width: `${Math.min(100, (budgetPct / 15.0) * 100)}%` }}
          />
        </div>

        {/* Rule verification */}
        <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
          <span>Constraint: Min 1 segment &ge; 4.0s:</span>
          <span className={hasSegmentGe4s ? 'text-emerald-400 font-semibold' : 'text-amber-400 font-semibold'}>
            {hasSegmentGe4s ? 'PASSED (valid)' : 'WARNING (< 4.0s)'}
          </span>
        </div>
      </div>

      {/* Segment Cards */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {highlights.map((hl, i) => {
          const segLen = hl.segment[1] - hl.segment[0];
          const isActive = currentTime >= hl.segment[0] && currentTime <= hl.segment[1];

          return (
            <div
              key={i}
              onClick={() => onSeek(hl.segment[0])}
              className={`p-2.5 rounded-lg border transition-all cursor-pointer flex items-center justify-between text-xs select-none ${
                isActive
                  ? 'bg-cyan-500/15 border-cyan-400/60 shadow-sm shadow-cyan-500/10'
                  : 'bg-surface-100/70 border-border/80 hover:bg-surface-200/80 hover:border-slate-600'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onSeek(hl.segment[0]);
                  }}
                  className={`h-6 w-6 rounded flex items-center justify-center transition-colors ${
                    isActive
                      ? 'bg-cyan-400 text-slate-950 font-bold'
                      : 'bg-surface-200 text-slate-400 hover:bg-cyan-500 hover:text-white'
                  }`}
                  title="Jump to segment"
                >
                  <Play className="h-3 w-3 ml-0.5 fill-current" />
                </button>

                <div>
                  <div className="font-semibold text-slate-200">
                    Segment #{i + 1}
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    [{hl.segment[0].toFixed(1)}s - {hl.segment[1].toFixed(1)}s]
                  </div>
                </div>
              </div>

              <div className="text-right">
                <span className="font-mono text-cyan-300 font-semibold">
                  {segLen.toFixed(1)}s
                </span>
                {hl.importance !== undefined && (
                  <div className="text-[10px] text-slate-400 font-mono">
                    imp: {Math.round(hl.importance * 100)}%
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

