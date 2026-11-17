import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  fetchVideoResult 
} from '../services/api';
import { VideoAnalysisResult } from '../types';
import { VideoPlayer } from '../components/video/VideoPlayer';
import { ActionTimeline } from '../components/timeline/ActionTimeline';
import { InteractionGraph } from '../components/graph/InteractionGraph';
import { HighlightInspector } from '../components/highlights/HighlightInspector';
import { ExportPanel } from '../components/export/ExportPanel';
import { 
  Layers, 
  Sparkles, 
  Network, 
  FileCode2, 
  Clock, 
  ChevronRight
} from 'lucide-react';

export const VideoWorkspace: React.FC = () => {
  const { videoId = 'P02_109' } = useParams<{ videoId: string }>();

  const [result, setResult] = useState<VideoAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [isHighlightMode, setIsHighlightMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'graph' | 'export'>('graph');

  useEffect(() => {
    setLoading(true);
    fetchVideoResult(videoId)
      .then((data) => {
        setResult(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load video result:', err);
        setLoading(false);
      });
  }, [videoId]);

  if (loading || !result) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="flex flex-col items-center space-y-3">
          <div className="h-8 w-8 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
          <span className="text-xs text-slate-400 font-mono">
            Loading EgoWeave Studio for {videoId}...
          </span>
        </div>
      </div>
    );
  }

  const { metadata, submission, graph, stats } = result;

  const videoSrc = isHighlightMode && metadata.highlight_url
    ? metadata.highlight_url
    : metadata.video_url;

  return (
    <div className="flex flex-col h-full max-w-[1700px] mx-auto space-y-4">
      {/* Top Breadcrumb & Metadata Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-border/80">
        <div className="flex items-center space-x-2 text-xs">
          <Link to="/" className="text-slate-400 hover:text-slate-200">
            Overview
          </Link>
          <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
          <Link to="/library" className="text-slate-400 hover:text-slate-200">
            Library
          </Link>
          <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
          <span className="font-semibold text-slate-100 font-mono">{metadata.video_id}</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-200 text-cyan-400 uppercase font-medium">
            {metadata.dataset}
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
            Label: {submission.label.name} ({Math.round(submission.label.score * 100)}%)
          </span>
        </div>

        {/* Quick KPI pills */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-surface-100 border border-border">
            <Clock className="h-3.5 w-3.5 text-cyan-400" />
            <span className="text-slate-400">Duration:</span>
            <span className="font-mono text-slate-200 font-semibold">{metadata.duration_sec.toFixed(1)}s</span>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-surface-100 border border-border">
            <Sparkles className="h-3.5 w-3.5 text-amber-400" />
            <span className="text-slate-400">Summary:</span>
            <span className="font-mono text-slate-200 font-semibold">{stats.highlight_duration_sec.toFixed(1)}s</span>
            <span className="font-mono text-cyan-400 font-bold">({stats.highlight_percentage.toFixed(1)}%)</span>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-surface-100 border border-border">
            <Layers className="h-3.5 w-3.5 text-blue-400" />
            <span className="text-slate-400">Actions:</span>
            <span className="font-mono text-slate-200 font-semibold">{submission.actions.length}</span>
          </div>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1 min-h-0 overflow-hidden">
        {/* Left Column (7 cols): Synced Video Player + Lower Tab (Interaction Graph or JSON Export) */}
        <div className="lg:col-span-7 flex flex-col space-y-4 overflow-y-auto pr-1">
          <VideoPlayer
            src={videoSrc}
            duration={metadata.duration_sec}
            highlights={submission.highlights}
            actions={submission.actions}
            currentTime={currentTime}
            onTimeUpdate={setCurrentTime}
            onSeek={setCurrentTime}
            videoTitle={`${metadata.video_id} (${metadata.width}x${metadata.height} @ ${metadata.fps}fps)`}
            isHighlightMode={isHighlightMode}
          />

          <div className="flex flex-col flex-1 min-h-[360px] bg-surface-50 border border-border rounded-xl overflow-hidden">
            <div className="px-3 pt-2 bg-[#0b0f19] border-b border-border flex items-center space-x-2">
              <button
                onClick={() => setActiveTab('graph')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-t-lg text-xs font-semibold transition-colors border-t border-x ${
                  activeTab === 'graph'
                    ? 'bg-surface-50 text-cyan-400 border-border border-b-transparent'
                    : 'text-slate-400 hover:text-slate-200 border-transparent'
                }`}
              >
                <Network className="h-3.5 w-3.5" />
                <span>Temporal Interaction Graph</span>
              </button>

              <button
                onClick={() => setActiveTab('export')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-t-lg text-xs font-semibold transition-colors border-t border-x ${
                  activeTab === 'export'
                    ? 'bg-surface-50 text-blue-400 border-border border-b-transparent'
                    : 'text-slate-400 hover:text-slate-200 border-transparent'
                }`}
              >
                <FileCode2 className="h-3.5 w-3.5" />
                <span>Official JSON Output</span>
              </button>
            </div>

            <div className="flex-1 overflow-hidden">
              {activeTab === 'graph' ? (
                <InteractionGraph
                  graphData={graph}
                  currentTime={currentTime}
                  onSeek={setCurrentTime}
                />
              ) : (
                <ExportPanel
                  submission={submission}
                  highlightUrl={metadata.highlight_url}
                />
              )}
            </div>
          </div>
        </div>

        {/* Right Column (5 cols): Action Timeline + Highlight Inspector */}
        <div className="lg:col-span-5 flex flex-col space-y-4 overflow-y-auto">
          <div className="h-[360px] min-h-[300px]">
            <ActionTimeline
              actions={submission.actions}
              highlights={submission.highlights}
              currentTime={currentTime}
              onSeek={setCurrentTime}
            />
          </div>

          <div className="flex-1 min-h-[300px]">
            <HighlightInspector
              highlights={submission.highlights}
              durationSec={metadata.duration_sec}
              currentTime={currentTime}
              onSeek={setCurrentTime}
              isHighlightMode={isHighlightMode}
              onToggleHighlightMode={() => setIsHighlightMode(!isHighlightMode)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
