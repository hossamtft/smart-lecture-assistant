import { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import { getTopicMap, detectTopics } from '../services/api';
import './TopicMap.css';

interface TopicMapProps {
  moduleCode: string;
}

export default function TopicMap({ moduleCode }: TopicMapProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topicsCount, setTopicsCount] = useState(0);

  const loadTopicMap = useCallback(async () => {
    if (!moduleCode) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getTopicMap(moduleCode);

      // Convert to ReactFlow format
      const flowNodes: Node[] = data.nodes.map((node, index) => {
        // Circular layout
        const angle = (index / data.nodes.length) * 2 * Math.PI;
        const radius = 250;
        const x = Math.cos(angle) * radius + 400;
        const y = Math.sin(angle) * radius + 300;

        return {
          id: node.id,
          data: { label: node.label },
          position: { x, y },
          style: {
            background: node.color || '#646cff',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 20px',
            fontSize: '14px',
            fontWeight: '600',
            width: Math.max(100, node.size * 20),
            textAlign: 'center'
          },
          sourcePosition: Position.Right,
          targetPosition: Position.Left
        };
      });

      const flowEdges: Edge[] = data.edges.map((edge, index) => ({
        id: `edge-${index}`,
        source: edge.source,
        target: edge.target,
        type: edge.type === 'prerequisite' ? 'smoothstep' : 'default',
        animated: edge.type === 'prerequisite',
        label: edge.type === 'prerequisite' ? 'prerequisite' : undefined,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#646cff'
        },
        style: {
          stroke: edge.type === 'prerequisite' ? '#646cff' : '#999',
          strokeWidth: 2
        },
        labelStyle: {
          fontSize: '10px',
          fill: '#666'
        }
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
      setTopicsCount(data.nodes.length);

    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to load topic map');
    } finally {
      setLoading(false);
    }
  }, [moduleCode]);

  useEffect(() => {
    loadTopicMap();
  }, [loadTopicMap]);

  const handleDetectTopics = async () => {
    if (!moduleCode) return;

    setDetecting(true);
    setError(null);

    try {
      const response = await detectTopics(moduleCode);
      setTopicsCount(response.topics_detected);

      // Reload the topic map
      await loadTopicMap();

    } catch (error: any) {
      setError(error.response?.data?.detail || 'Topic detection failed');
    } finally {
      setDetecting(false);
    }
  };

  if (!moduleCode) {
    return (
      <div className="topic-map-empty">
        <p>Select a module to view topic map</p>
      </div>
    );
  }

  return (
    <div className="topic-map-container">
      {/* Header */}
      <div className="topic-map-header">
        <div>
          <h2>Topic Map: {moduleCode}</h2>
          {topicsCount > 0 && (
            <p className="topics-count">{topicsCount} topics detected</p>
          )}
        </div>
        <button
          onClick={handleDetectTopics}
          disabled={detecting}
          className="detect-btn"
        >
          {detecting ? 'Detecting...' : 'Run Topic Detection'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="topic-map-loading">
          <div className="loading-spinner"></div>
          <p>Loading topic map...</p>
        </div>
      ) : nodes.length === 0 ? (
        <div className="topic-map-empty">
          <span className="empty-icon">🔍</span>
          <p>No topics detected yet</p>
          <p className="empty-hint">
            Click "Run Topic Detection" to analyze your lectures and identify cross-lecture topics.
          </p>
        </div>
      ) : (
        <div className="topic-map-flow">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            attributionPosition="bottom-left"
          >
            <Controls />
            <Background color="#aaa" gap={16} />
          </ReactFlow>

          {/* Legend */}
          <div className="topic-map-legend">
            <h4>Legend</h4>
            <div className="legend-item">
              <div className="legend-line animated"></div>
              <span>Prerequisite relationship</span>
            </div>
            <div className="legend-item">
              <div className="legend-node"></div>
              <span>Topic (size = frequency)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
