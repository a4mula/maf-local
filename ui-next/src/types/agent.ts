// Agent types and status definitions
export type AgentTier = 'liaison' | 'project-lead' | 'domain-lead' | 'executor';
export type AgentStatus = 'active' | 'waiting' | 'idle' | 'error';

export interface AgentNode {
    [key: string]: unknown; // Index signature for React Flow compatibility
    id: string;
    name: string;
    tier: AgentTier;
    status: AgentStatus;
    currentTask?: string;
    metrics: {
        tokensUsed: number;
        timeInState: number; // seconds
        messagesProcessed: number;
    };
}

export interface AgentConnection {
    from: string;
    to: string;
    message?: string;
    active: boolean; // whether data is currently flowing
}

export interface AgentGraphData {
    nodes: AgentNode[];
    connections: AgentConnection[];
    lastUpdated: string;
}
