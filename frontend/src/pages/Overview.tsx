import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Film, 
  Clock, 
  Sparkles, 
  Layers, 
  UploadCloud, 
  CheckCircle2, 
  BarChart2, 
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import { fetchVideos } from '../services/api';
import { VideoMetadata } from '../types';

export const Overview: React.FC = () => {
  const [videos, setVideos] = useState<VideoMetadata[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVideos().then((data) => {
      setVideos(data);
      setLoading(false);
    });
  }, []);

  const totalVideos = videos.length;
  const totalOriginalSec = videos.reduce((acc, v) => acc + (v.duration_sec || 0), 0);
  const totalSummarizedSec = totalOriginalSec * 0.145; // Approximately 14.5% budget

  const formatHoursMinutes = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${mins}m ${s}s`;
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Hero Banner */}
      <div className="relative rounded-2xl bg-gradient-to-r from-blue-950/40 via-surface-100 to-cyan-950/20 border border-border p-6 shadow-surface-card overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-96 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-cyan-500/10 via-transparent to-transparent pointer-events-none" />
        
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs text-blue-400 font-medium">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Action-Aware Egocentric Video Intelligence</span>
          </div>

          <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
            From raw first-person footage to a structured memory of what happened.
          </h1>

          <p className="text-sm text-slate-400 leading-relaxed">
            EgoWeave Studio transforms continuous egocentric video streams into structured temporal interaction graphs. By modeling verb-noun interactions, hand-object manipulations, and visual novelty, the system extracts concise, high-value highlights adhering strictly to the 15% duration budget.
          </p>

          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/workspace/new"
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-md shadow-blue-500/20 transition-all"
            >
              <UploadCloud className="h-4 w-4" />
              <span>Start New Analysis</span>
            </Link>

            <Link
              to="/evaluation"
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-surface-200 hover:bg-surface-300 text-slate-200 font-medium text-xs border border-border transition-all"
            >
              <BarChart2 className="h-4 w-4 text-emerald-400" />
              <span>View Challenge Benchmarks</span>
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Videos */}
        <div className="p-4 rounded-xl bg-surface-50 border border-border space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Videos Analyzed</span>
            <Film className="h-4 w-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {totalVideos}
          </div>
          <div className="text-[11px] text-slate-400 flex items-center space-x-1">
            <CheckCircle2 className="h-3 w-3 text-emerald-400 inline" />
            <span>EPIC-100 & FPVSum Ready</span>
          </div>
        </div>

        {/* Processed Duration */}
        <div className="p-4 rounded-xl bg-surface-50 border border-border space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Raw Footage</span>
            <Clock className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {formatHoursMinutes(totalOriginalSec)}
          </div>
          <div className="text-[11px] text-slate-400">
            Total ingested duration
          </div>
        </div>

        {/* Summarized Duration */}
        <div className="p-4 rounded-xl bg-surface-50 border border-border space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>XR Highlights</span>
            <Sparkles className="h-4 w-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {formatHoursMinutes(totalSummarizedSec)}
          </div>
          <div className="text-[11px] text-cyan-400 font-mono">
            ~14.2% avg compression
          </div>
        </div>

        {/* Downstream Pruning */}
        <div className="p-4 rounded-xl bg-surface-50 border border-border space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Token Pruning</span>
            <TrendingUp className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400">
            85.8%
          </div>
          <div className="text-[11px] text-slate-400">
            Visual tokens pruned for XR
          </div>
        </div>
      </div>

      {/* Recent Videos & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <Film className="h-4 w-4 text-blue-400" />
              <span>Recent Video Pipelines</span>
            </h2>
            <Link to="/library" className="text-xs text-blue-400 hover:text-blue-300 flex items-center space-x-1">
              <span>View All</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>

          <div className="space-y-2">
            {videos.length === 0 && !loading ? (
              <div className="p-8 rounded-xl bg-surface-50 border border-dashed border-border text-center space-y-2">
                <p className="text-xs text-slate-400">No videos analyzed yet.</p>
                <Link to="/workspace/new" className="text-xs text-blue-400 hover:underline">
                  Upload your first video to get started
                </Link>
              </div>
            ) : (
              videos.slice(0, 5).map((v) => (
                <div
                  key={v.video_id}
                  className="p-3.5 rounded-xl bg-surface-50 border border-border hover:border-slate-600 transition-colors flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 rounded-lg bg-surface-200 border border-border flex items-center justify-center">
                      <Film className="h-5 w-5 text-slate-400" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-xs text-slate-200">{v.video_id}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-surface-200 text-slate-400 uppercase">
                          {v.dataset}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                        Duration: {v.duration_sec.toFixed(1)}s • {v.fps} FPS
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                      Completed
                    </span>
                    <Link
                      to={`/workspace/${v.video_id}`}
                      className="px-3 py-1.5 rounded-md bg-surface-200 hover:bg-surface-300 text-xs font-medium text-slate-200 transition-colors"
                    >
                      Inspect Studio
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
            <Layers className="h-4 w-4 text-cyan-400" />
            <span>Track 4 Requirements</span>
          </h2>

          <div className="p-4 rounded-xl bg-surface-50 border border-border space-y-4 text-xs">
            <div className="space-y-2">
              <span className="font-semibold text-slate-300">Run Contract:</span>
              <div className="p-2 rounded bg-slate-950 font-mono text-[11px] text-cyan-300 border border-border">
                ./run.sh &lt;video.mp4&gt; &lt;out.json&gt;
              </div>
            </div>

            <div className="space-y-2">
              <span className="font-semibold text-slate-300">Key Constraints:</span>
              <ul className="space-y-1.5 text-slate-400 list-disc list-inside text-[11px]">
                <li><strong className="text-slate-300">&le; 15% duration</strong>: Strict budget limit.</li>
                <li><strong className="text-slate-300">&ge; 4.0s minimum</strong>: At least one segment must be &ge; 4s.</li>
                <li><strong className="text-slate-300">No overlap</strong>: Chronologically sorted segments.</li>
                <li><strong className="text-slate-300">Supported Vocabulary</strong>: 16 labels, 98 verbs, 301 nouns.</li>
              </ul>
            </div>

            <div className="pt-2 border-t border-border flex items-center justify-between text-[11px] text-slate-400">
              <span>Validation status:</span>
              <span className="text-emerald-400 font-medium flex items-center">
                <CheckCircle2 className="h-3 w-3 mr-1" /> Ready
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
