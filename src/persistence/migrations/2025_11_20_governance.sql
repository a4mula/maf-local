-- Governance decisions table
CREATE TABLE IF NOT EXISTS governance_decisions (
    decision_id UUID PRIMARY KEY,
    category VARCHAR(50),  -- 'architecture', 'constraint', 'vision'
    content JSONB,
    created_at TIMESTAMP,
    created_by VARCHAR(50),  -- 'ProjectLead'
    immutable BOOLEAN DEFAULT true
);

-- Drift detection log
CREATE TABLE IF NOT EXISTS drift_log (
    drift_id UUID PRIMARY KEY,
    decision_id UUID REFERENCES governance_decisions(decision_id),
    detected_at TIMESTAMP,
    severity VARCHAR(20),  -- 'low', 'medium', 'high'
    description TEXT
);
