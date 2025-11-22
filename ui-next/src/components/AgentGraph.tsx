'use client';

import { useCallback, useEffect, useState } from 'react';
import {
    ReactFlow,
    Node,
    Edge,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    BackgroundVariant,
    MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import AgentNodeComponent from './AgentNode';
import { AgentGraphData } from '@/types/agent';

const nodeTypes = {
    agentNode: AgentNodeComponent,
} as any; // Type assertion to avoid strict typing issues with React Flow

// Helper to avoid hydration errors with time
function useHasMounted() {
    const [hasMounted, setHasMounted] = useState(false);
    useEffect(() => {
        setHasMounted(true);
    }, []);
    return hasMounted;
}

// Mock data removed. Initial state is empty.
const initialGraphData: AgentGraphData = {
    nodes: [],
    connections: [],
    lastUpdated: new Date().toISOString(),
};

function convertToReactFlowNodes(graphData: AgentGraphData): Node[] {
    return graphData.nodes.map((node, index) => ({
        id: node.id,
        type: 'agentNode',
        position: calculateNodePosition(node.tier, index),
        data: node,
    }));
}

function convertToReactFlowEdges(graphData: AgentGraphData): Edge[] {
    return graphData.connections.map((conn, index) => ({
        id: `${conn.from}-${conn.to}`,
        source: conn.from,
        target: conn.to,
        animated: conn.active,
        style: {
            stroke: conn.active ? '#4CAF50' : '#666',
            strokeWidth: conn.active ? 3 : 2,
        },
        markerEnd: {
            type: MarkerType.ArrowClosed,
            color: conn.active ? '#4CAF50' : '#666',
        },
        label: conn.message,
        labelStyle: { fill: '#fff', fontSize: 10 },
        labelBgStyle: { fill: '#333', fillOpacity: 0.8 },
    }));
}

// Calculate node positions in a hierarchical layout
function calculateNodePosition(tier: string, index: number) {
    const tierYPositions = {
        'liaison': 50,
        'project-lead': 200,
        'domain-lead': 350,
        'executor': 500,
    };

    const tierXOffsets = {
        'liaison': 400,
        'project-lead': 400,
        'domain-lead': 200 + index * 250,
        'executor': 200 + index * 250,
    };

    return {
        x: tierXOffsets[tier as keyof typeof tierXOffsets] || 400,
        y: tierYPositions[tier as keyof typeof tierYPositions] || 100,
    };
}

export default function AgentGraph() {
    const hasMounted = useHasMounted();
    const [graphData, setGraphData] = useState<AgentGraphData>(initialGraphData);
    const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch agent data from API
    const fetchAgentData = useCallback(async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8002';
            const response = await fetch(`${apiUrl}/api/agents/status`);
            if (!response.ok) throw new Error('Failed to fetch agent status');
            const data = await response.json();
            setGraphData(data);
            setError(null);
        } catch (error) {
            console.error('Failed to fetch agent data:', error);
            setError('Failed to connect to Agent API');
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Update graph when data changes
    useEffect(() => {
        setNodes(convertToReactFlowNodes(graphData));
        setEdges(convertToReactFlowEdges(graphData));
    }, [graphData, setNodes, setEdges]);

    // Poll for updates every 2 seconds
    useEffect(() => {
        fetchAgentData(); // Initial fetch
        const interval = setInterval(fetchAgentData, 2000);
        return () => clearInterval(interval);
    }, [fetchAgentData]);

    if (!hasMounted) return null;

    return (
        <div className="w-full h-screen bg-[#1a1a1a] relative">
            {/* Header Bar */}
            <div className="absolute top-0 left-0 right-0 bg-gray-900 bg-opacity-90 p-4 border-b border-gray-800 z-10 flex justify-between items-center">
                <h1 className="text-xl font-bold text-white">Hierarchical MAF Studio</h1>
                <div className="flex gap-6 text-sm">
                    <div className="flex items-center gap-2">
                        <span className="text-gray-400">Project:</span>
                        <span className="font-mono text-green-400">
                            {(graphData as any).activeContext?.project_name || 'DevStudio (Self)'}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-gray-400">Session:</span>
                        <span className="font-mono text-blue-400">
                            {(graphData as any).activeContext?.session_name || 'None'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            {isLoading && nodes.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-400">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
                        <p>Connecting to Agent Neural Network...</p>
                    </div>
                </div>
            ) : error ? (
                <div className="flex items-center justify-center h-full text-red-400">
                    <div className="text-center">
                        <p className="text-xl mb-2">⚠️ Connection Lost</p>
                        <p className="text-sm opacity-75">{error}</p>
                    </div>
                </div>
            ) : (
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    nodeTypes={nodeTypes}
                    fitView
                    minZoom={0.5}
                    maxZoom={1.5}
                    className="bg-[#1a1a1a]"
                >
                    <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#333" />
                    <Controls className="!bg-gray-800 !border-gray-700" />
                </ReactFlow>
            )}

            {/* Status bar */}
            <div className="absolute bottom-4 left-4 bg-gray-900 bg-opacity-90 px-4 py-2 rounded-lg text-sm z-10">
                <div className="flex items-center gap-4 text-gray-300">
                    <span className={error ? "text-red-500" : "text-green-500"}>
                        {error ? "🔴 Offline" : "🟢 Online"}
                    </span>
                    <span className="text-gray-600">|</span>
                    <span>Agents: {graphData.nodes.filter(n => n.status === 'active').length} Active</span>
                    <span className="text-gray-600">|</span>
                    <span>Last Updated: {new Date(graphData.lastUpdated).toLocaleTimeString()}</span>
                </div>
            </div>
        </div>
    );
}
