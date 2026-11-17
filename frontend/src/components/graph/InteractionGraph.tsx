import React, { useMemo, useCallback } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { InteractionGraphData, GraphNodeData } from '../../types';
import { Network, Sparkles, Clock } from 'lucide-react';

interface InteractionGraphProps {
  graphData: InteractionGraphData;
  currentTime?: number;
  onSeek: (time: number) => void;
}

// Custom Node component for egocentric actions
const ActionNode: React.FC<{ data: GraphNodeData }> = ({ data }) => {
  return (
    <div
      className={`px-3 py-2 rounded-xl border transition-all cursor-pointer select-none min-w-[130px] ${
        data.isHighlight
          ? 'bg-slate-900 border-cyan-400/80 shadow-md shadow-cyan-500/20 ring-1 ring-cyan-400/40'
          : 'bg-slate-900/90 border-border hover:border-slate-500'
      }`}
    >
      <Handle type="target" position={Position.Left} className="!bg-cyan-400 !w-2 !h-2" />
      
      <div className="flex items-center justify-between gap-1 text-[10px] text-slate-400 font-mono mb-1">
        <span className="flex items-center space-x-1">
          <Clock className="h-2.5 w-2.5 text-slate-400" />
          <span>{data.start.toFixed(1)}s</span>
        </span>
        {data.isHighlight && (
          <span className="text-cyan-400 flex items-center font-semibold">
            <Sparkles className="h-2.5 w-2.5 mr-0.5" /> 15%
          </span>
        )}
      </div>

      <div className="text-xs font-semibold text-slate-100 flex items-center space-x-1">
        <span className="text-blue-400">{data.verb}</span>
        <span className="text-slate-400">•</span>
        <span className="text-cyan-300">{data.noun}</span>
      </div>

      <div className="mt-1 flex items-center justify-between text-[10px]">
        <span className="text-slate-400">conf</span>
        <span className="font-mono text-slate-300 font-medium">
          {Math.round(data.score * 100)}%
        </span>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-blue-500 !w-2 !h-2" />
    </div>
  );
};

export const InteractionGraph: React.FC<InteractionGraphProps> = ({
  graphData,
  onSeek,
}) => {
  const nodeTypes = useMemo(() => ({ actionNode: ActionNode }), []);

  // Format nodes for React Flow
  const initialNodes: Node[] = useMemo(() => {
    return graphData.nodes.map((n) => ({
      id: n.id,
      position: n.position,
      type: 'actionNode',
      data: n.data,
    }));
  }, [graphData.nodes]);

  // Format edges
  const initialEdges: Edge[] = useMemo(() => {
    return graphData.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      animated: e.animated ?? true,
      style: {
        stroke: e.data?.type === 'shared_noun' ? '#38bdf8' : '#64748b',
        strokeWidth: 2,
      },
      label: e.data?.label,
      labelStyle: { fill: '#94a3b8', fontSize: 10, fontFamily: 'monospace' },
      labelBgStyle: { fill: '#0f172a', rx: 4, ry: 4 },
    }));
  }, [graphData.edges]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const nodeData = node.data as unknown as GraphNodeData;
      if (nodeData && typeof nodeData.start === 'number') {
        onSeek(nodeData.start);
      }
    },
    [onSeek]
  );

  return (
    <div className="flex flex-col h-full bg-surface-50 border border-border rounded-xl overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b border-border bg-[#0b0f19] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Network className="h-4 w-4 text-cyan-400" />
          <span className="text-xs font-semibold text-slate-200">Temporal Interaction Graph</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-200 text-slate-400">
            {nodes.length} nodes • {edges.length} relations
          </span>
        </div>
        <div className="flex items-center space-x-2 text-[11px] text-slate-400">
          <span className="flex items-center space-x-1">
            <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
            <span>Shared Object Edge</span>
          </span>
          <span className="text-slate-600">•</span>
          <span className="flex items-center space-x-1">
            <span className="h-2 w-2 rounded-full bg-slate-500"></span>
            <span>Temporal Sequence</span>
          </span>
        </div>
      </div>

      {/* React Flow Canvas */}
      <div className="flex-1 w-full h-full min-h-[280px] bg-[#070a10]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-right"
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#1e293b" />
          <Controls className="!bg-surface-100 !border-border !fill-slate-300" />
          <MiniMap
            nodeStrokeColor="#38bdf8"
            nodeColor="#1e293b"
            maskColor="rgba(8, 11, 17, 0.7)"
            className="!bg-surface-50 !border !border-border rounded-lg"
          />
        </ReactFlow>
      </div>
    </div>
  );
};
