export type DatasetType = 'epic_kitchens_100' | 'fpvsum' | 'custom';

export type JobStatus = 'queued' | 'extracting_metadata' | 'sampling_frames' | 'detecting_actions' | 'building_graph' | 'ranking_highlights' | 'compiling_output' | 'completed' | 'failed';

export interface ActionPrediction {
  segment: [number, number];
  verb: string;
  noun: string;
  score: number;
  importance?: number;
}

export interface HighlightSegment {
  segment: [number, number];
  importance?: number;
}

export interface VideoLabel {
  name: string;
  score: number;
}

export interface VideoSubmissionOutput {
  team_id: string;
  video_id: string;
  duration_sec: number;
  label: VideoLabel;
  actions: ActionPrediction[];
  highlights: HighlightSegment[];
}

export interface GraphNodeData {
  id: string;
  label: string;
  verb: string;
  noun: string;
  start: number;
  end: number;
  score: number;
  isHighlight: boolean;
  [key: string]: unknown;
}

export interface GraphEdgeData {
  id: string;
  source: string;
  target: string;
  type: 'temporal' | 'shared_noun' | 'repeated_action' | 'transition';
  label?: string;
  [key: string]: unknown;
}

export interface InteractionGraphData {
  nodes: Array<{
    id: string;
    position: { x: number; y: number };
    data: GraphNodeData;
    type?: string;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    type?: string;
    animated?: boolean;
    style?: Record<string, unknown>;
    data?: GraphEdgeData;
  }>;
}

export interface VideoMetadata {
  video_id: string;
  filename: string;
  duration_sec: number;
  width: number;
  height: number;
  fps: number;
  dataset: DatasetType;
  file_size_mb: number;
  status: JobStatus;
  job_id: string;
  created_at: string;
  thumbnail_url?: string;
  video_url: string;
  highlight_url?: string;
  result_json_url?: string;
}

export interface VideoAnalysisResult {
  metadata: VideoMetadata;
  submission: VideoSubmissionOutput;
  graph: InteractionGraphData;
  stats: {
    total_actions_count: number;
    unique_action_pairs_count: number;
    highlight_duration_sec: number;
    highlight_percentage: number;
    budget_compliance: boolean;
    max_single_highlight_sec: number;
    min_single_highlight_sec: number;
    processing_time_sec: number;
  };
}

export interface JobProgressEvent {
  job_id: string;
  video_id: string;
  status: JobStatus;
  progress: number;
  current_step: string;
  error?: string;
  timestamp: string;
}

export interface EvaluationMetricReport {
  team_id: string;
  evaluated_videos_count: number;
  epic_videos_count: number;
  fpvsum_videos_count: number;
  action_coverage: number;
  action_map: number;
  highlight_f1: number;
  label_accuracy: number;
  total_score: number;
  budget_compliance_rate: number;
  average_inference_time_sec: number;
  per_video_results: Array<{
    video_id: string;
    dataset: DatasetType;
    duration_sec: number;
    highlight_pct: number;
    action_count: number;
    status: 'evaluated' | 'no_ground_truth';
    coverage_score?: number;
    map_score?: number;
    f1_score?: number;
    label_correct?: boolean;
  }>;
}

