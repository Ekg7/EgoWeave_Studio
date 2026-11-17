import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  UploadCloud, 
  CheckCircle2, 
  AlertCircle,
  Layers
} from 'lucide-react';
import { checkBackendHealth } from '../../services/api';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [health, setHealth] = useState<{ status: string; gpu_available: boolean; device: string }>({
    status: 'checking',
    gpu_available: false,
    device: 'cpu'
  });

  useEffect(() => {
    checkBackendHealth().then(setHealth);
    const interval = setInterval(() => {
      checkBackendHealth().then(setHealth);
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const isOnline = health.status === 'ok' || health.status === 'healthy';

  return (
    <header className="h-14 border-b border-border bg-[#0b0f19]/80 backdrop-blur-md px-4 flex items-center justify-between select-none z-30">
      {/* Brand Identity */}
      <div className="flex items-center space-x-3">
        <Link to="/" className="flex items-center space-x-2.5 group">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 p-[1px] shadow-sm shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-shadow">
            <div className="h-full w-full bg-slate-950 rounded-[7px] flex items-center justify-center">
              <Layers className="h-4 w-4 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-sm tracking-tight text-white">EgoWeave Studio</span>
            </div>
            <p className="text-[11px] text-slate-400 font-normal leading-none hidden sm:block">
              Action-Aware Egocentric Video Intelligence
            </p>
          </div>
        </Link>
      </div>

      {/* Center Product Identity */}
      <div className="hidden md:flex items-center space-x-2 px-3 py-1 rounded-full bg-surface-100 border border-border text-xs text-slate-300">
        <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
        <span className="font-medium text-slate-200">Action-Aware Video Intelligence</span>
        <span className="text-slate-600">•</span>
        <span className="text-slate-400 font-mono text-[11px]">≤ 15% Duration Budget</span>
      </div>

      {/* Right Controls & Health */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-1.5 text-xs px-2.5 py-1 rounded bg-surface-100 border border-border">
          {isOnline ? (
            <>
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-slate-300 font-medium">Engine Active</span>
              <span className="text-[10px] font-mono text-slate-400 uppercase">({health.device})</span>
            </>
          ) : (
            <>
              <AlertCircle className="h-3.5 w-3.5 text-amber-400" />
              <span className="text-slate-300 font-medium">Standby / Local</span>
            </>
          )}
        </div>

        {location.pathname !== '/workspace/new' && (
          <Link
            to="/workspace/new"
            className="flex items-center space-x-1.5 text-xs font-medium px-3 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white shadow-sm shadow-blue-500/20 transition-colors"
          >
            <UploadCloud className="h-3.5 w-3.5" />
            <span>Analyze Video</span>
          </Link>
        )}
      </div>
    </header>
  );
};
