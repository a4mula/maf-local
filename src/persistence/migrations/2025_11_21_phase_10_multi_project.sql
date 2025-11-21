-- Phase 10 Migration: Multi-Project Support

-- 1. Create projects table
CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    workspace_path VARCHAR(512) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB DEFAULT '{}'
);

-- 2. Insert DevStudio as Project 0 (read-only)
INSERT INTO projects (project_id, name, description, workspace_path, metadata)
VALUES (0, 'maf-local', 'DevStudio System (Read-Only)', '/app', '{"read_only": true}')
ON CONFLICT (project_id) DO NOTHING;

-- 3. Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id INTEGER NOT NULL REFERENCES projects(project_id),
    user_id VARCHAR(255) DEFAULT 'default_user',
    status VARCHAR(50) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    context JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- 4. Add project_id to existing tables (if not exists)
DO $$ 
BEGIN 
    -- audit_logs
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        agent_name VARCHAR(255),
        action VARCHAR(255),
        details JSONB,
        project_id INTEGER DEFAULT 0 REFERENCES projects(project_id)
    );
    
    -- Add project_id if table existed but column didn't (idempotency)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='audit_logs' AND column_name='project_id') THEN
        ALTER TABLE audit_logs ADD COLUMN project_id INTEGER DEFAULT 0 REFERENCES projects(project_id);
    END IF;
    
    CREATE INDEX IF NOT EXISTS idx_audit_logs_project_id ON audit_logs(project_id);

    -- governance_decisions
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='governance_decisions' AND column_name='project_id') THEN
        ALTER TABLE governance_decisions ADD COLUMN project_id INTEGER DEFAULT 0 REFERENCES projects(project_id);
        CREATE INDEX idx_governance_project_id ON governance_decisions(project_id);
    END IF;

    -- checkpoints
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='workflow_checkpoints' AND column_name='project_id') THEN
        ALTER TABLE workflow_checkpoints ADD COLUMN project_id INTEGER DEFAULT 0 REFERENCES projects(project_id);
        CREATE INDEX idx_checkpoints_project_id ON workflow_checkpoints(project_id);
    END IF;
END $$;
