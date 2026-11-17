import React, { useRef, useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  SkipBack, 
  SkipForward,
  Sparkles,
  Layers
} from 'lucide-react';
import { HighlightSegment, ActionPrediction } from '../../types';

interface VideoPlayerProps {
  src: string;
  duration?: number;
  highlights?: HighlightSegment[];
  actions?: ActionPrediction[];
  currentTime: number;
  onTimeUpdate: (time: number) => void;
  onSeek: (time: number) => void;
  videoTitle?: string;
  isHighlightMode?: boolean;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  src,
  duration = 0,
  highlights = [],
  actions = [],
  currentTime,
  onTimeUpdate,
  onSeek,
  videoTitle = 'Original Egocentric Footage',
  isHighlightMode = false,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const progressBarRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [actualDuration, setActualDuration] = useState(duration);

  // Sync external seek
  useEffect(() => {
    if (videoRef.current && Math.abs(videoRef.current.currentTime - currentTime) > 0.5) {
      videoRef.current.currentTime = currentTime;
    }
  }, [currentTime]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play().catch(e => console.warn('Play interrupted:', e));
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      onTimeUpdate(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setActualDuration(videoRef.current.duration || duration);
    }
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current) return;
    const rect = progressBarRef.current.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    const targetTime = Math.max(0, Math.min(pos * (actualDuration || duration || 1), actualDuration || duration));
    if (videoRef.current) {
      videoRef.current.currentTime = targetTime;
    }
    onSeek(targetTime);
  };

  const stepTime = (delta: number) => {
    if (!videoRef.current) return;
    const target = Math.max(0, Math.min(videoRef.current.currentTime + delta, actualDuration || duration));
    videoRef.current.currentTime = target;
    onSeek(target);
  };

  const handleRateChange = (rate: number) => {
    setPlaybackRate(rate);
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
    }
  };

  const formatTimestamp = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    const ms = Math.floor((sec % 1) * 10);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}.${ms}`;
  };

  const totalDur = actualDuration || duration || 1;
  const progressPct = Math.min(100, Math.max(0, (currentTime / totalDur) * 100));

  return (
    <div className="flex flex-col bg-slate-950 rounded-xl border border-border overflow-hidden shadow-surface-card">
      {/* Player Header */}
      <div className="px-4 py-2.5 bg-surface-50 border-b border-border flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <span className={`h-2 w-2 rounded-full ${isHighlightMode ? 'bg-cyan-400' : 'bg-blue-500'}`}></span>
          <span className="font-semibold text-slate-200">{videoTitle}</span>
          {isHighlightMode && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-medium flex items-center space-x-1">
              <Sparkles className="h-3 w-3 inline mr-1" />
              15% XR Highlight Stream
            </span>
          )}
        </div>
        <div className="flex items-center space-x-3 text-slate-400 font-mono text-[11px]">
          <span>{formatTimestamp(currentTime)} / {formatTimestamp(totalDur)}</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400">{playbackRate}x</span>
        </div>
      </div>

      {/* Video Viewport */}
      <div className="relative aspect-video bg-black flex items-center justify-center group overflow-hidden">
        <video
          ref={videoRef}
          src={src}
          className="w-full h-full object-contain"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onClick={togglePlay}
          playsInline
        />

        {/* Big play overlay if paused */}
        {!isPlaying && (
          <button
            onClick={togglePlay}
            className="absolute inset-0 m-auto h-16 w-16 rounded-full bg-blue-600/80 hover:bg-blue-600 text-white flex items-center justify-center shadow-lg backdrop-blur-sm transition-transform hover:scale-110 z-10"
            title="Play video"
          >
            <Play className="h-7 w-7 ml-1" />
          </button>
        )}

        {/* Current Active Action Pill on Video */}
        {actions.length > 0 && (() => {
          const activeAction = actions.find(
            a => currentTime >= a.segment[0] && currentTime <= a.segment[1]
          );
          if (!activeAction) return null;
          return (
            <div className="absolute top-3 left-3 z-10 bg-black/75 backdrop-blur-md border border-cyan-500/40 px-3 py-1.5 rounded-lg flex items-center space-x-2 text-xs text-white shadow-lg animate-pulse-subtle">
              <Layers className="h-3.5 w-3.5 text-cyan-400" />
              <div>
                <span className="font-semibold text-cyan-300 uppercase tracking-wider text-[10px] mr-1">Action:</span>
                <span className="font-medium">{activeAction.verb} {activeAction.noun}</span>
                <span className="ml-1.5 text-slate-400 font-mono text-[10px]">({Math.round(activeAction.score * 100)}%)</span>
              </div>
            </div>
          );
        })()}
      </div>

      {/* Custom Scrubber with Highlight Overlays */}
      <div 
        ref={progressBarRef}
        onClick={handleProgressClick}
        className="relative h-4 bg-surface-200 cursor-pointer select-none border-y border-border group"
      >
        {/* Highlight Interval Shading */}
        {highlights.map((hl, i) => {
          const startPct = (hl.segment[0] / totalDur) * 100;
          const endPct = (hl.segment[1] / totalDur) * 100;
          const widthPct = Math.max(0.5, endPct - startPct);
          return (
            <div
              key={i}
              style={{ left: `${startPct}%`, width: `${widthPct}%` }}
              className="absolute top-0 bottom-0 bg-cyan-500/35 border-x border-cyan-400/50 hover:bg-cyan-500/50 transition-colors"
              title={`Highlight [${hl.segment[0]}s - ${hl.segment[1]}s]`}
            />
          );
        })}

        {/* Action Ticks */}
        {actions.map((act, i) => {
          const actPos = (act.segment[0] / totalDur) * 100;
          return (
            <div
              key={i}
              style={{ left: `${actPos}%` }}
              className="absolute top-0 bottom-0 w-[2px] bg-amber-400/70 pointer-events-none"
              title={`${act.verb} ${act.noun}`}
            />
          );
        })}

        {/* Active playback progress */}
        <div
          style={{ width: `${progressPct}%` }}
          className="absolute top-0 bottom-0 bg-blue-500/70 pointer-events-none"
        />

        {/* Scrubber thumb */}
        <div
          style={{ left: `${progressPct}%` }}
          className="absolute top-0 bottom-0 w-1.5 bg-white shadow-md -translate-x-1/2 pointer-events-none group-hover:scale-y-125 transition-transform"
        />
      </div>

      {/* Control Bar */}
      <div className="px-4 py-2 bg-surface-50 flex items-center justify-between text-slate-300">
        <div className="flex items-center space-x-2">
          <button
            onClick={togglePlay}
            className="p-1.5 rounded-md hover:bg-surface-200 text-slate-200 transition-colors"
            title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
          >
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>

          <button
            onClick={() => stepTime(-5)}
            className="p-1.5 rounded-md hover:bg-surface-200 text-slate-400 hover:text-slate-200 transition-colors"
            title="Rewind 5s (←)"
          >
            <SkipBack className="h-4 w-4" />
          </button>

          <button
            onClick={() => stepTime(5)}
            className="p-1.5 rounded-md hover:bg-surface-200 text-slate-400 hover:text-slate-200 transition-colors"
            title="Forward 5s (→)"
          >
            <SkipForward className="h-4 w-4" />
          </button>

          <div className="h-4 w-[1px] bg-border mx-1" />

          <button
            onClick={() => {
              const nextMute = !isMuted;
              setIsMuted(nextMute);
              if (videoRef.current) videoRef.current.muted = nextMute;
            }}
            className="p-1.5 rounded-md hover:bg-surface-200 text-slate-400 hover:text-slate-200 transition-colors"
          >
            {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
          </button>
        </div>

        {/* Speed selectors */}
        <div className="flex items-center space-x-1 text-xs">
          {[0.5, 1, 1.5, 2].map((rate) => (
            <button
              key={rate}
              onClick={() => handleRateChange(rate)}
              className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                playbackRate === rate
                  ? 'bg-blue-600/30 text-blue-400 border border-blue-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-surface-100'
              }`}
            >
              {rate}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
