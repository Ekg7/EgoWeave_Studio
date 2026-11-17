import React, { useEffect, useState } from 'react';
import { 
  BarChart3, 
  FileCheck2,
  TrendingUp
} from 'lucide-react';
import { fetchEvaluationMetrics } from '../services/api';
import { EvaluationMetricReport } from '../types';

export const Evaluation: React.FC = () => {
  const [report, setReport] = useState<EvaluationMetricReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvaluationMetrics().then((data) => {
      setReport(data);
      setLoading(false);
    });
  }, []);

  if (loading || !report) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-xs text-slate-400 font-mono">Loading Evaluation Lab...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
          <BarChart3 className="h-5 w-5 text-emerald-400" />
          <span>Evaluation Lab & Challenge Benchmark</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Official Samsung PRISM Track 4 metrics calculated against ground-truth validation splits (EPIC-KITCHENS-100 & FPVSum).
        </p>
      </div>

      {/* Official 100-Point Formula Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Action Coverage (40%) */}
        <div className="p-4 rounded-xl bg-surface-50 border border-border space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200">Action Coverage</span>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Weight: 40%
            </span>
          </div>
          <div className="text-3xl font-bold font-mono text-cyan-400">
            {(report.action_coverage * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-slate-400">
            Distinct GT action pairs captured inside &le;15% highlights.
          </p>
        </div>

        {/* Action mAP (25%) */}
        <div className="p-4 rounded-xl bg-surface-50 border border-border space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200">Action mAP</span>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Weight: 25%
            </span>
          </div>
          <div className="text-3xl font-bold font-mono text-blue-400">
            {(report.action_map * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-slate-400">
            Verb-noun temporal overlap across tIoU thresholds [0.1–0.5].
          </p>
        </div>

        {/* Highlight F1 (25%) */}
        <div className="p-4 rounded-xl bg-surface-50 border border-border space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200">Highlight F1</span>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Weight: 25%
            </span>
          </div>
          <div className="text-3xl font-bold font-mono text-amber-400">
            {(report.highlight_f1 * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-slate-400">
            Frame-level F1 against consensus top-15% importance annotations.
          </p>
        </div>

        {/* Label Accuracy (10%) */}
        <div className="p-4 rounded-xl bg-surface-50 border border-border space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200">Label Accuracy</span>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Weight: 10%
            </span>
          </div>
          <div className="text-3xl font-bold font-mono text-emerald-400">
            {(report.label_accuracy * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-slate-400">
            Video-level activity categorization across 16 supported classes.
          </p>
        </div>
      </div>

      {/* Aggregate Score & Compliance Banner */}
      <div className="p-4 rounded-xl bg-surface-50 border border-border flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="h-12 w-12 rounded-xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <TrendingUp className="h-6 w-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Composite Challenge Score (100 pts)</div>
            <div className="text-2xl font-bold font-mono text-white">
              {report.total_score.toFixed(2)} / 100.00
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
          <div className="p-2.5 rounded-lg bg-surface-100 border border-border">
            <span className="text-slate-400">Budget Compliance: </span>
            <span className="text-emerald-400 font-semibold">{report.budget_compliance_rate}%</span>
          </div>

          <div className="p-2.5 rounded-lg bg-surface-100 border border-border">
            <span className="text-slate-400">Avg Inference Time: </span>
            <span className="text-cyan-400 font-semibold">{report.average_inference_time_sec}s / video</span>
          </div>

          <div className="p-2.5 rounded-lg bg-surface-100 border border-border">
            <span className="text-slate-400">Evaluated Videos: </span>
            <span className="text-slate-200 font-semibold">{report.evaluated_videos_count}</span>
          </div>
        </div>
      </div>

      {/* Per-Video Results Table */}
      <div className="rounded-xl bg-surface-50 border border-border overflow-hidden space-y-0">
        <div className="p-3 bg-[#0b0f19] border-b border-border flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileCheck2 className="h-4 w-4 text-blue-400" />
            <span className="text-xs font-semibold text-slate-200">Per-Video Validation Ledger</span>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">
            {report.per_video_results.length} records
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-100/70 border-b border-border text-[11px] text-slate-400 uppercase font-mono">
              <tr>
                <th className="px-4 py-2.5">Video ID</th>
                <th className="px-4 py-2.5">Dataset</th>
                <th className="px-4 py-2.5">Duration</th>
                <th className="px-4 py-2.5">Highlight %</th>
                <th className="px-4 py-2.5">Actions</th>
                <th className="px-4 py-2.5">Action Coverage</th>
                <th className="px-4 py-2.5">Action mAP</th>
                <th className="px-4 py-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60 font-mono">
              {report.per_video_results.map((row) => (
                <tr key={row.video_id} className="hover:bg-surface-100/50 transition-colors">
                  <td className="px-4 py-3 font-semibold text-slate-200">
                    {row.video_id}
                  </td>
                  <td className="px-4 py-3 text-cyan-400 uppercase text-[11px]">
                    {row.dataset}
                  </td>
                  <td className="px-4 py-3 text-slate-300">
                    {row.duration_sec.toFixed(1)}s
                  </td>
                  <td className="px-4 py-3 text-cyan-300 font-semibold">
                    {row.highlight_pct.toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 text-slate-300">
                    {row.action_count}
                  </td>
                  <td className="px-4 py-3 text-slate-200">
                    {row.coverage_score !== undefined
                      ? `${(row.coverage_score * 100).toFixed(1)}%`
                      : <span className="text-slate-500 text-[10px]">Ground truth unavailable</span>}
                  </td>
                  <td className="px-4 py-3 text-slate-200">
                    {row.map_score !== undefined
                      ? `${(row.map_score * 100).toFixed(1)}%`
                      : <span className="text-slate-500 text-[10px]">Ground truth unavailable</span>}
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                      {row.status === 'evaluated' ? 'Evaluated' : 'Unlabeled (Submission)'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
