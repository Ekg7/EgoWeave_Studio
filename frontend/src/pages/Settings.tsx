import React, { useEffect, useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Cpu, 
  Server, 
  CheckCircle2, 
  Sliders,
  ShieldCheck
} from 'lucide-react';
import { checkBackendHealth } from '../services/api';

export const Settings: React.FC = () => {
  const [health, setHealth] = useState<{ status: string; version: string; gpu_available: boolean; device: string }>({
    status: 'checking',
    version: '1.0.0',
    gpu_available: false,
    device: 'cpu'
  });

  const [targetBudget, setTargetBudget] = useState(14.5);
  const [minSegmentDuration, setMinSegmentDuration] = useState(4.0);
  const [nmsThreshold, setNmsThreshold] = useState(0.4);

  useEffect(() => {
    checkBackendHealth().then(setHealth);
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
          <SettingsIcon className="h-5 w-5 text-blue-400" />
          <span>System Settings & Architecture Profiling</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Hardware acceleration profile, inference configuration, and official submission compliance thresholds.
        </p>
      </div>

      <div className="p-5 rounded-2xl bg-surface-50 border border-border space-y-4">
        <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
          <Server className="h-4 w-4 text-cyan-400" />
          <span>Backend & Engine Diagnostics</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-surface-100 border border-border space-y-1">
            <span className="text-slate-400">Connection Status:</span>
            <div className="flex items-center space-x-1.5 font-semibold text-slate-200">
              <span className={`h-2 w-2 rounded-full ${health.status === 'ok' || health.status === 'healthy' ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              <span className="capitalize">{health.status}</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-surface-100 border border-border space-y-1">
            <span className="text-slate-400">Execution Hardware:</span>
            <div className="flex items-center space-x-1.5 font-semibold text-slate-200 uppercase font-mono">
              <Cpu className="h-3.5 w-3.5 text-blue-400" />
              <span>{health.device}</span>
              {health.gpu_available && <span className="text-emerald-400 text-[10px]">(CUDA)</span>}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-surface-100 border border-border space-y-1">
            <span className="text-slate-400">EgoWeave Core Version:</span>
            <div className="font-mono font-semibold text-slate-200">
              v{health.version} (Prism Track 4)
            </div>
          </div>
        </div>
      </div>

      <div className="p-5 rounded-2xl bg-surface-50 border border-border space-y-4">
        <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
          <Sliders className="h-4 w-4 text-emerald-400" />
          <span>Inference & Optimization Thresholds</span>
        </h2>

        <div className="space-y-4 text-xs">
          <div className="p-3 rounded-xl bg-surface-100 border border-border space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-200">Highlight Target Budget:</span>
                <p className="text-[11px] text-slate-400">
                  Target total duration constraint for video summary (Safety margin under 15.0% limit).
                </p>
              </div>
              <span className="font-mono font-bold text-cyan-400 text-sm">{targetBudget}%</span>
            </div>
            <input
              type="range"
              min="10.0"
              max="15.0"
              step="0.1"
              value={targetBudget}
              onChange={(e) => setTargetBudget(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-surface-300 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
          </div>

          <div className="p-3 rounded-xl bg-surface-100 border border-border space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-200">Minimum Segment Duration Constraint:</span>
                <p className="text-[11px] text-slate-400">
                  Official rule requires at least one highlight segment &ge; 4.0s (segments &lt; 4s ignored).
                </p>
              </div>
              <span className="font-mono font-bold text-blue-400 text-sm">{minSegmentDuration.toFixed(1)}s</span>
            </div>
            <input
              type="range"
              min="2.0"
              max="6.0"
              step="0.5"
              value={minSegmentDuration}
              onChange={(e) => setMinSegmentDuration(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-surface-300 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          <div className="p-3 rounded-xl bg-surface-100 border border-border space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-200">Temporal Non-Maximum Suppression (tIoU):</span>
                <p className="text-[11px] text-slate-400">
                  Overlap suppression threshold for adjacent multi-scale sliding window action predictions.
                </p>
              </div>
              <span className="font-mono font-bold text-amber-400 text-sm">{nmsThreshold.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="0.8"
              step="0.05"
              value={nmsThreshold}
              onChange={(e) => setNmsThreshold(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-surface-300 rounded-lg appearance-none cursor-pointer accent-amber-400"
            />
          </div>
        </div>
      </div>

      <div className="p-5 rounded-2xl bg-surface-50 border border-border space-y-3">
        <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
          <ShieldCheck className="h-4 w-4 text-cyan-400" />
          <span>Submission Contract & Official Schema</span>
        </h2>
        <div className="p-3 rounded-xl bg-slate-950 border border-border text-xs text-slate-300 space-y-2">
          <div className="flex items-center space-x-2 text-emerald-400 font-mono text-[11px]">
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>Strict 6-key JSON verified by validate.py</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Keys: <code className="text-cyan-300">team_id</code>, <code className="text-cyan-300">video_id</code>, <code className="text-cyan-300">duration_sec</code>, <code className="text-cyan-300">label</code>, <code className="text-cyan-300">actions</code>, <code className="text-cyan-300">highlights</code>.
          </p>
          <p className="text-[11px] text-slate-400">
            Zero-hardcoding policy: all predictions generated dynamically through <code className="text-slate-200">inference/pipeline.py</code> and verified against <code className="text-slate-200">manifest.csv</code> and <code className="text-slate-200">supported_classes.json</code>.
          </p>
        </div>
      </div>
    </div>
  );
};
