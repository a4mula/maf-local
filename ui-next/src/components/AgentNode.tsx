'use client';

import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { AgentNode as AgentNodeData } from '@/types/agent';
import { cn } from '@/lib/utils';

// Color mapping for tiers and statuses
const tierColors = {
    'liaison': 'bg-tier-liaison',
    'project-lead': 'bg-tier-pl',
    'domain-lead': 'bg-tier-dl',
    'executor': 'bg-tier-executor',
};

const statusColors = {
    'active': 'ring-agent-active',
    'waiting': 'ring-agent-waiting',
    'idle': 'ring-agent-idle',
    'error': 'ring-agent-error',
};

const statusIcons = {
    'active': '🟢',
    'waiting': '🟡',
    'idle': '⚪',
    'error': '🔴',
};

interface CustomNodeData extends AgentNodeData {
    label?: string;
}

function AgentNodeComponent({ data }: NodeProps<CustomNodeData>) {
    const { name, tier, status, currentTask, metrics } = data;

    // Determine node size based on tier (Liaison > PL > DL > Executor)
    const sizeClass = tier === 'liaison'
        ? 'w-32 h-32'
        : tier === 'project-lead'
            ? 'w-28 h-28'
            : tier === 'domain-lead'
                ? 'w-24 h-24'
                : 'w-20 h-20';

    return (
        <div
            className={cn(
                'rounded-full flex flex-col items-center justify-center',
                'text-white font-semibold shadow-lg',
                'ring-4 transition-all duration-300',
                sizeClass,
                tierColors[tier],
                statusColors[status],
                status === 'active' && 'animate-pulse'
            )}
        >
            {/* Connection handles */}
            <Handle
                type="target"
                position={Position.Top}
                className="w-3 h-3 !bg-gray-400"
            />

            {/* Node content */}
            <div className="text-center px-2">
                <div className="text-xs mb-1">{statusIcons[status]}</div>
                <div className="text-sm font-bold leading-tight">{name}</div>
                {currentTask && (
                    <div className="text-[10px] mt-1 opacity-80 line-clamp-2">
                        {currentTask}
                    </div>
                )}
                {metrics && (
                    <div className="text-[9px] mt-1 opacity-60">
                        {metrics.tokensUsed}t | {Math.floor(metrics.timeInState)}s
                    </div>
                )}
            </div>

            {/* Connection handles */}
            <Handle
                type="source"
                position={Position.Bottom}
                className="w-3 h-3 !bg-gray-400"
            />
        </div>
    );
}

export default memo(AgentNodeComponent);
