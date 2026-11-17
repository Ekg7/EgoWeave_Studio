import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Film, 
  Search, 
  Filter, 
  ArrowUpRight, 
  UploadCloud
} from 'lucide-react';
import { fetchVideos } from '../services/api';
import { VideoMetadata } from '../types';

export const Library: React.FC = () => {
  const [videos, setVideos] = useState<VideoMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedDataset, setSelectedDataset] = useState<string>('all');

  useEffect(() => {
    fetchVideos().then((data) => {
      setVideos(data);
      setLoading(false);
    });
  }, []);

  const filteredVideos = videos.filter((v) => {
    const matchesSearch = v.video_id.toLowerCase().includes(search.toLowerCase()) ||
                          v.filename.toLowerCase().includes(search.toLowerCase());
    const matchesDataset = selectedDataset === 'all' || v.dataset === selectedDataset;
    return matchesSearch && matchesDataset;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Title & Action */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
            <Film className="h-5 w-5 text-blue-400" />
            <span>Processed Video Library</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Browse, inspect, and export all analyzed egocentric videos across EPIC-KITCHENS-100 and FPVSum.
          </p>
        </div>

        <Link
          to="/workspace/new"
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-md shadow-blue-500/20 transition-colors"
        >
          <UploadCloud className="h-4 w-4" />
          <span>Upload New Video</span>
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3 rounded-xl bg-surface-50 border border-border flex flex-wrap items-center justify-between gap-3">
        <div className="relative flex-1 min-w-[240px] max-w-md">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by video ID or filename..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-surface-100 border border-border rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <Filter className="h-3.5 w-3.5 text-slate-400" />
          <span className="text-slate-400">Dataset:</span>
          {['all', 'epic_kitchens_100', 'fpvsum', 'custom'].map((ds) => (
            <button
              key={ds}
              onClick={() => setSelectedDataset(ds)}
              className={`px-2.5 py-1 rounded-md text-xs font-mono transition-colors ${
                selectedDataset === ds
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold'
                  : 'bg-surface-100 text-slate-400 hover:text-slate-200 hover:bg-surface-200'
              }`}
            >
              {ds === 'all' ? 'All' : ds}
            </button>
          ))}
        </div>
      </div>

      {/* Video Cards Grid */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400 font-mono">
          Loading library videos...
        </div>
      ) : filteredVideos.length === 0 ? (
        <div className="p-12 rounded-2xl bg-surface-50 border border-dashed border-border text-center space-y-2">
          <p className="text-xs text-slate-400">No videos match your criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredVideos.map((v) => {
            const highlightBudgetPct = 14.25;
            return (
              <div
                key={v.video_id}
                className="group rounded-xl bg-surface-50 border border-border hover:border-slate-600 transition-all overflow-hidden flex flex-col justify-between shadow-sm"
              >
                <div className="p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-sm text-white font-mono group-hover:text-blue-400 transition-colors">
                          {v.video_id}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-surface-200 text-cyan-400 uppercase font-medium">
                          {v.dataset}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 font-mono mt-0.5 truncate max-w-[220px]">
                        {v.filename}
                      </p>
                    </div>

                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                      Completed
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-400">
                    <div className="p-2 rounded bg-surface-100 flex items-center justify-between">
                      <span>Duration:</span>
                      <span className="text-slate-200">{v.duration_sec.toFixed(1)}s</span>
                    </div>
                    <div className="p-2 rounded bg-surface-100 flex items-center justify-between">
                      <span>Highlight:</span>
                      <span className="text-cyan-400 font-bold">{highlightBudgetPct}%</span>
                    </div>
                  </div>
                </div>

                <div className="px-4 py-2.5 bg-surface-100 border-t border-border flex items-center justify-between text-xs">
                  <span className="text-[10px] text-slate-400 font-mono">
                    {new Date(v.created_at).toLocaleDateString()}
                  </span>

                  <Link
                    to={`/workspace/${v.video_id}`}
                    className="inline-flex items-center space-x-1 text-blue-400 hover:text-blue-300 font-medium group-hover:translate-x-0.5 transition-transform"
                  >
                    <span>Open in Studio</span>
                    <ArrowUpRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
