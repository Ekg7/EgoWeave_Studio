import React, { useState } from 'react';
import { ActionPrediction, HighlightSegment } from '../../types';
import { Search, Clock, Play, Sparkles } from 'lucide-react';

interface ActionTimelineProps {
  actions: ActionPrediction[];
  highlights?: HighlightSegment[];
  currentTime: number;
  onSeek: (time: number) => void;
}

export const ActionTimeline: React.FC<ActionTimelineProps> = ({
  actions,
  highlights = [],
  currentTime,
  onSeek,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredActions = actions.filter(
    (a) =>
      a.verb.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.noun.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const isInsideHighlight = (start: number, end: number) => {
    return highlights.some(
      (h) => (start >= h.segment[0] && start <= h.segment[1]) ||
             (end >= h.segment[0] && end <= h.segment[1])
    );
  };

  return (
    <div className="flex flex-col h-full bg-surface-50 border border-border rounded-xl overflow-hidden">
      {/* Header & Search */}
      <div className="p-3 border-b border-border bg-[#0b0f19] flex items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <Clock className="h-4 w-4 text-cyan-400" />
          <span className="text-xs font-semibold text-slate-200">Temporal Actions</span>
          <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-surface-200 text-slate-400">
            {actions.length} detected
          </span>
        </div>

        {/* Filter input */}
        <div className="relative w-44">
          <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Filter actions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-surface-100 border border-border rounded-md pl-8 pr-2.5 py-1 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Action List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {filteredActions.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-400">
            {actions.length === 0
              ? 'No temporal action predictions generated yet.'
              : 'No actions match the current filter.'}
          </div>
        ) : (
          filteredActions.map((action, idx) => {
            const isActive = currentTime >= action.segment[0] && currentTime <= action.segment[1];
            const inHighlight = isInsideHighlight(action.segment[0], action.segment[1]);
            const duration = (action.segment[1] - action.segment[0]).toFixed(1);

            return (
              <div
                key={idx}
                onClick={() => onSeek(action.segment[0])}
                className={`group p-2.5 rounded-lg border transition-all cursor-pointer flex items-center justify-between text-xs select-none ${
                  isActive
                    ? 'bg-blue-600/15 border-blue-500/50 shadow-sm shadow-blue-500/10'
                    : 'bg-surface-100/70 border-border/80 hover:bg-surface-200/80 hover:border-slate-600'
                }`}
              >
                {/* Left: Verb & Noun */}
                <div className="flex items-center space-x-2.5">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSeek(action.segment[0]);
                    }}
                    className={`h-6 w-6 rounded flex items-center justify-center transition-colors ${
                      isActive
                        ? 'bg-blue-500 text-white'
                        : 'bg-surface-200 text-slate-400 group-hover:bg-blue-600 group-hover:text-white'
                    }`}
                    title="Jump to action"
                  >
                    <Play className="h-3 w-3 ml-0.5 fill-current" />
                  </button>

                  <div>
                    <div className="flex items-center space-x-1.5">
                      <span className="font-semibold text-slate-200 group-hover:text-blue-300">
                        {action.verb}
                      </span>
                      <span className="text-slate-400 font-mono text-[11px]">•</span>
                      <span className="font-medium text-cyan-300">
                        {action.noun}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 mt-0.5 text-[10px] text-slate-400 font-mono">
                      <span>[{action.segment[0].toFixed(1)}s - {action.segment[1].toFixed(1)}s]</span>
                      <span>({duration}s)</span>
                    </div>
                  </div>
                </div>

                {/* Right: Confidence Score & Highlight Badge */}
                <div className="flex items-center space-x-2">
                  {inHighlight && (
                    <span className="flex items-center space-x-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20" title="Selected in highlight summary">
                      <Sparkles className="h-2.5 w-2.5" />
                      <span>Highlight</span>
                    </span>
                  )}

                  <div className="text-right">
                    <div className="text-[11px] font-mono font-medium text-slate-300">
                      {Math.round(action.score * 100)}%
                    </div>
                    <div className="w-12 h-1.5 bg-surface-300 rounded-full overflow-hidden mt-0.5">
                      <div
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${Math.round(action.score * 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
