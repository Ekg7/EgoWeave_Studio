import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Workflow, 
  Film, 
  BarChart3, 
  Settings, 
  FileCheck2
} from 'lucide-react';

interface SidebarProps {
  currentVideoId?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentVideoId }) => {
  const activeVideo = currentVideoId || 'P02_109';

  return (
    <aside className="w-60 border-r border-border bg-[#0b0f19] flex flex-col justify-between select-none">
      <div className="p-3 space-y-6">
        <div className="space-y-1">
          <div className="px-3 pb-1 text-[10px] font-semibold tracking-wider text-slate-400 uppercase font-mono">
            Platform
          </div>
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center space-x-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-surface-100'
              }`
            }
          >
            <LayoutDashboard className="h-4 w-4" />
            <span>Overview</span>
          </NavLink>

          <NavLink
            to="/workspace/new"
            className={({ isActive }) =>
              `flex items-center space-x-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-surface-100'
              }`
            }
          >
            <UploadCloud className="h-4 w-4" />
            <span>New Video Analysis</span>
          </NavLink>

          <NavLink
            to={`/workspace/${activeVideo}`}
            className={({ isActive }) =>
              `flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-surface-100'
              }`
            }
          >
            <div className="flex items-center space-x-2.5">
              <Workflow className="h-4 w-4 text-cyan-400" />
              <span>Studio Workspace</span>
            </div>
            {currentVideoId && (
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-surface-200 text-slate-300">
                Active
              </span>
            )}
          </NavLink>

          <NavLink
            to="/library"
            className={({ isActive }) =>
              `flex items-center space-x-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-surface-100'
              }`
            }
          >
            <Film className="h-4 w-4" />
            <span>Video Library</span>
          </NavLink>
        </div>

        <div className="space-y-1">
          <div className="px-3 pb-1 text-[10px] font-semibold tracking-wider text-slate-400 uppercase font-mono">
            Analysis Tools
          </div>
          <NavLink
            to="/evaluation"
            className={({ isActive }) =>
              `flex items-center space-x-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-surface-100'
              }`
            }
          >
            <BarChart3 className="h-4 w-4 text-emerald-400" />
            <span>Evaluation Lab</span>
          </NavLink>

          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `flex items-center space-x-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-surface-100'
              }`
            }
          >
            <Settings className="h-4 w-4" />
            <span>System Settings</span>
          </NavLink>
        </div>

        <div className="p-3 rounded-lg bg-surface-50 border border-border space-y-2">
          <div className="flex items-center justify-between text-[11px] font-medium text-slate-300">
            <span>Metric Weights</span>
            <FileCheck2 className="h-3.5 w-3.5 text-blue-400" />
          </div>
          <div className="space-y-1.5 text-[10px] text-slate-400">
            <div className="flex justify-between">
              <span>Action Coverage:</span>
              <span className="font-mono text-cyan-400 font-semibold">40%</span>
            </div>
            <div className="flex justify-between">
              <span>Action mAP:</span>
              <span className="font-mono text-slate-300 font-semibold">25%</span>
            </div>
            <div className="flex justify-between">
              <span>Highlight F1:</span>
              <span className="font-mono text-slate-300 font-semibold">25%</span>
            </div>
            <div className="flex justify-between">
              <span>Label Accuracy:</span>
              <span className="font-mono text-slate-300 font-semibold">10%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-3 border-t border-border/80 text-[11px] text-slate-400 space-y-1 bg-surface-50">
        <div className="flex items-center justify-between">
          <span className="font-medium text-slate-300">EgoWeave v1.0</span>
          <span className="text-[10px] font-mono px-1 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Official Contract
          </span>
        </div>
        <p className="text-[10px] text-slate-400 leading-tight">
          Validated with validate.py for EPIC-100 & FPVSum
        </p>
      </div>
    </aside>
  );
};
