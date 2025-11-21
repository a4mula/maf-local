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

// Mock data for demonstration
const initialGraphData: AgentGraphData = {
    nodes: [
        {
            id: 'liaison',
            name: 'Liaison',
            tier: 'liaison',
            status: 'active',
            currentTask: 'Processing user request...',
            metrics: { tokensUsed: 1250, timeInState: 5, messagesProcessed: 3 },
        },
        {
            id: 'pl',
            name: 'Project Lead',
            tier: 'project-lead',
            status: 'active',
            currentTask: 'Creating workflow',
            metrics: { tokensUsed: 3420, timeInState: 12, messagesProcessed: 7 },
        },
        {
            id: 'dev-dl',
            name: 'Dev DL',
            tier: 'domain-lead',
            status: 'active',
            currentTask: 'Delegating tasks',
            metrics: { tokensUsed: 890, timeInState: 8, messagesProcessed: 2 },
        },
        {
            id: 'qa-dl',
            name: 'QA DL',
            tier: 'domain-lead',
            status: 'idle',
            currentTask: undefined,
            metrics: { tokensUsed: 0, timeInState: 120, messagesProcessed: 0 },
        },
        {
            id: 'docs-dl',
            name: 'Docs DL',
            tier: 'domain-lead',
            status: 'idle',
            currentTask: undefined,
            metrics: { tokensUsed: 0, timeInState: 120, messagesProcessed: 0 },
        },
        {
            id: 'exec-coder',
            name: 'Coder',
            tier: 'executor',
            status: 'active',
            currentTask: 'Writing auth.py',
            metrics: { tokensUsed: 2100, timeInState: 45, messagesProcessed: 5 },
        },
        {
            id: 'exec-tester',
            name: 'Tester',
            tier: 'executor',
            status: 'idle',
            currentTask: undefined,
            metrics: { tokensUsed: 0, timeInState: 90, messagesProcessed: 0 },
        },
    ],
    connections: [
        { from: 'liaison', to: 'pl', message: 'Build auth API', active: true },
        { from: 'pl', to: 'dev-dl', message: 'Plan assigned', active: true },
        { from: 'pl', to: 'qa-dl', active: false },
        { from: 'pl', to: 'docs-dl', active: false },
        { from: 'dev-dl', to: 'exec-coder', message: 'Task: Create endpoints', active: true },
        { from: 'dev-dl', to: 'exec-tester', active: false },
    ],
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
    const [nodes, setNodes, onNodesChange] = useNodesState(convertToReactFlowNodes(initialGraphData));
    const [edges, setEdges, onEdgesChange] = useEdgesState(convertToReactFlowEdges(initialGraphData));

    // Fetch agent data from API
    const fetchAgentData = useCallback(async () => {
        try {
            const response = await fetch('http://localhost:8002/api/agents/status');
            if (!response.ok) throw new Error('Failed to fetch agent status');
            const data = await response.json();
            setGraphData(data);
        } catch (error) {
            console.error('Failed to fetch agent data:', error);
        }
    }, []);

    // Update graph when data changes
    useEffect(() => {
        setNodes(convertToReactFlowNodes(graphData));
        setEdges(convertToReactFlowEdges(graphData));
    }, [graphData, setNodes, setEdges]);

    // Poll for updates every 2 seconds
    useEffect(() => {
        const interval = setInterval(fetchAgentData, 2000);
        return () => clearInterval(interval);
    }, [fetchAgentData]);

    return (
        <div className="w-full h-screen bg-[#1a1a1a]">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                fitView
                minZoom={0.5}
                maxZoom={1.5}
            >
                <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#333" />
                <Controls className="!bg-gray-800 !border-gray-700" />
            </ReactFlow>

            {/* Status bar */}
            <div className="absolute bottom-4 left-4 bg-gray-900 bg-opacity-90 px-4 py-2 rounded-lg text-sm">
                <div className="flex items-center gap-4">
                    <span>🟢 All Systems Operational</span>
                    <span>|</span>
                    <span>Agents: {graphData.nodes.filter(n => n.status === 'active').length} Active</span>
                    <span>|</span>
                    <span>Last Updated: {hasMounted ? new Date(graphData.lastUpdated).toLocaleTimeString() : '--:--:--'}</span>
                </div>
            </div>
        </div>
    );
}
