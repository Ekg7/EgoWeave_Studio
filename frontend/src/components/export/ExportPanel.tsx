import React, { useState } from 'react';
import { VideoSubmissionOutput } from '../../types';
import { Download, Copy, Check, FileCode2, Video, CheckCircle2 } from 'lucide-react';

interface ExportPanelProps {
  submission: VideoSubmissionOutput;
  highlightUrl?: string;
}

export const ExportPanel: React.FC<ExportPanelProps> = ({
  submission,
  highlightUrl,
}) => {
  const [copied, setCopied] = useState(false);

  const jsonString = JSON.stringify(submission, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJson = () => {
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${submission.video_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full bg-surface-50 border border-border rounded-xl overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b border-border bg-[#0b0f19] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileCode2 className="h-4 w-4 text-blue-400" />
          <span className="text-xs font-semibold text-slate-200">Official JSON & Export</span>
          <span className="flex items-center space-x-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="h-2.5 w-2.5" />
            <span>Strict 6-Key Schema</span>
          </span>
        </div>

        {/* Action buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1 px-2.5 py-1 rounded text-xs font-medium bg-surface-100 hover:bg-surface-200 text-slate-300 border border-border transition-colors"
          >
            {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            onClick={handleDownloadJson}
            className="flex items-center space-x-1 px-2.5 py-1 rounded text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white transition-colors"
          >
            <Download className="h-3 w-3" />
            <span>Download .json</span>
          </button>

          {highlightUrl && (
            <a
              href={highlightUrl}
              download={`${submission.video_id}_highlight.mp4`}
              className="flex items-center space-x-1 px-2.5 py-1 rounded text-xs font-medium bg-cyan-600 hover:bg-cyan-500 text-white transition-colors"
            >
              <Video className="h-3 w-3" />
              <span>Export MP4</span>
            </a>
          )}
        </div>
      </div>

      {/* JSON Viewer */}
      <div className="flex-1 p-3 overflow-y-auto bg-slate-950 font-mono text-[11px] text-slate-300 select-text">
        <pre className="whitespace-pre-wrap">{jsonString}</pre>
      </div>
    </div>
  );
};

