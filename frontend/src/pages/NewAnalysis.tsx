import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, 
  AlertCircle, 
  ArrowRight,
  FileVideo,
  Sparkles,
  Info
} from 'lucide-react';
import { uploadVideo, subscribeJobEvents } from '../services/api';
import { DatasetType, JobProgressEvent } from '../types';

export const NewAnalysis: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null);
  const [videoMeta, setVideoMeta] = useState<{ duration: number; width: number; height: number } | null>(null);
  const [detectedDataset, setDetectedDataset] = useState<DatasetType>('epic_kitchens_100');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Upload & processing state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [jobProgress, setJobProgress] = useState<JobProgressEvent | null>(null);

  const handleFileSelect = (file: File) => {
    setErrorMsg(null);
    if (!file.name.toLowerCase().endsWith('.mp4')) {
      setErrorMsg('Please select a valid MP4 video file (.mp4 format required).');
      return;
    }

    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > 1024) {
      setErrorMsg(`File size (${sizeMb.toFixed(1)} MB) exceeds the 1024 MB maximum limit.`);
      return;
    }

    setSelectedFile(file);

    const fname = file.name.toLowerCase();
    if (fname.startsWith('p') && fname.includes('_')) {
      setDetectedDataset('epic_kitchens_100');
    } else if (
      fname.includes('ski') || 
      fname.includes('bike') || 
      fname.includes('skate') || 
      fname.includes('scuba') || 
      fname.includes('surf')
    ) {
      setDetectedDataset('fpvsum');
    } else {
      setDetectedDataset('custom');
    }

    const url = URL.createObjectURL(file);
    setVideoPreviewUrl(url);

    const tempVideo = document.createElement('video');
    tempVideo.preload = 'metadata';
    tempVideo.src = url;
    tempVideo.onloadedmetadata = () => {
      setVideoMeta({
        duration: tempVideo.duration,
        width: tempVideo.videoWidth,
        height: tempVideo.videoHeight,
      });
    };
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleSubmitAnalysis = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setUploadProgress(0);
    setErrorMsg(null);

    try {
      const res = await uploadVideo(selectedFile, detectedDataset, (pct) => {
        setUploadProgress(pct);
      });

      setJobProgress({
        job_id: res.job_id,
        video_id: res.video_id,
        status: 'extracting_metadata',
        progress: 10,
        current_step: 'Extracting video metadata & temporal boundaries...',
        timestamp: new Date().toISOString(),
      });

      subscribeJobEvents(
        res.job_id,
        (evt) => {
          setJobProgress(evt);
          if (evt.status === 'completed') {
            setTimeout(() => {
              navigate(`/workspace/${evt.video_id}`);
            }, 1000);
          }
        },
        (err) => {
          console.warn('SSE fallback or error:', err);
          setTimeout(() => {
            navigate(`/workspace/${res.video_id}`);
          }, 3000);
        }
      );
    } catch (err: unknown) {
      setIsUploading(false);
      setErrorMsg(err instanceof Error ? err.message : 'Upload failed. Check backend connection.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
          <UploadCloud className="h-5 w-5 text-blue-400" />
          <span>New Video Analysis</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Upload an egocentric MP4 video to extract fine-grained actions, build the temporal interaction graph, and compile a 15% highlight summary.
        </p>
      </div>

      {errorMsg && (
        <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {!selectedFile ? (
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-border hover:border-blue-500/60 rounded-2xl p-12 bg-surface-50/50 hover:bg-surface-50 transition-all cursor-pointer text-center space-y-4 group select-none"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".mp4"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          />

          <div className="h-16 w-16 mx-auto rounded-2xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400 group-hover:scale-105 transition-transform">
            <UploadCloud className="h-8 w-8" />
          </div>

          <div className="space-y-1">
            <p className="text-sm font-semibold text-slate-200">
              Drag and drop your egocentric MP4 video here, or <span className="text-blue-400">browse</span>
            </p>
            <p className="text-xs text-slate-400">
              Supports EPIC-KITCHENS-100 & FPVSum benchmark formats (2–10 min recommended, up to 1GB)
            </p>
          </div>

          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-surface-100 border border-border text-[11px] text-slate-400">
            <Info className="h-3.5 w-3.5 text-cyan-400" />
            <span>Target summary automatically bounded to &le; 15% duration</span>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="p-5 rounded-2xl bg-surface-50 border border-border space-y-5">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="h-12 w-12 rounded-xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                  <FileVideo className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{selectedFile.name}</h3>
                  <div className="flex items-center space-x-3 text-xs text-slate-400 font-mono mt-0.5">
                    <span>{(selectedFile.size / (1024 * 1024)).toFixed(1)} MB</span>
                    <span>•</span>
                    <span>{videoMeta ? `${videoMeta.width}x${videoMeta.height}` : 'Reading resolution...'}</span>
                    <span>•</span>
                    <span>{videoMeta ? `${videoMeta.duration.toFixed(1)}s` : 'Reading duration...'}</span>
                  </div>
                </div>
              </div>

              {!isUploading && (
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setVideoPreviewUrl(null);
                    setVideoMeta(null);
                  }}
                  className="text-xs text-slate-400 hover:text-rose-400 transition-colors"
                >
                  Change Video
                </button>
              )}
            </div>

            {videoPreviewUrl && (
              <div className="rounded-xl overflow-hidden aspect-video bg-black max-h-72 border border-border">
                <video src={videoPreviewUrl} controls className="w-full h-full object-contain" />
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Target Benchmark Dataset:</label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {(['epic_kitchens_100', 'fpvsum', 'custom'] as DatasetType[]).map((ds) => (
                  <button
                    key={ds}
                    type="button"
                    onClick={() => setDetectedDataset(ds)}
                    disabled={isUploading}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      detectedDataset === ds
                        ? 'bg-blue-600/15 border-blue-500 text-white shadow-sm'
                        : 'bg-surface-100 border-border text-slate-400 hover:bg-surface-200'
                    }`}
                  >
                    <div className="text-xs font-semibold uppercase font-mono">
                      {ds === 'epic_kitchens_100' ? 'EPIC-KITCHENS-100' : ds === 'fpvsum' ? 'FPVSum' : 'Generic First-Person'}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      {ds === 'epic_kitchens_100'
                        ? 'Optimizes Action Coverage (40%) & mAP (25%)'
                        : ds === 'fpvsum'
                        ? 'Optimizes Highlight F1 (25%) & Category (10%)'
                        : 'General egocentric action detection'}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {isUploading && (
              <div className="p-4 rounded-xl bg-surface-100 border border-border space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-200 flex items-center space-x-2">
                    <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
                    <span>{jobProgress ? jobProgress.current_step : `Uploading footage (${uploadProgress}%)...`}</span>
                  </span>
                  <span className="font-mono text-cyan-400 font-bold">
                    {jobProgress ? `${jobProgress.progress}%` : `${uploadProgress}%`}
                  </span>
                </div>

                <div className="w-full h-2 bg-surface-300 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-300"
                    style={{ width: `${jobProgress ? jobProgress.progress : uploadProgress}%` }}
                  />
                </div>

                <div className="text-[11px] text-slate-400 flex items-center justify-between font-mono">
                  <span>Execution: Background Inference Worker</span>
                  <span>Target: &le; 15% highlight</span>
                </div>
              </div>
            )}

            {!isUploading && (
              <div className="flex justify-end pt-2">
                <button
                  onClick={handleSubmitAnalysis}
                  className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-md shadow-blue-500/20 transition-all"
                >
                  <Sparkles className="h-4 w-4" />
                  <span>Execute EgoWeave Analysis</span>
                  <ArrowRight className="h-4 w-4 ml-1" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
