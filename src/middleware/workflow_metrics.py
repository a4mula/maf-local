"""
Workflow Metrics Middleware

This module provides observability for the MAF-Local workflow engine.
It uses the Prometheus client library to expose metrics for:
- Workflow execution duration
- Agent execution counts
- Error rates
- Workflow success/failure status

It follows the Singleton pattern to ensure consistent metric registry.
"""

import time
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

# Configure logger
logger = logging.getLogger(__name__)

class WorkflowMetrics:
    """
    Singleton class for managing workflow metrics.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorkflowMetrics, cls).__new__(cls)
            cls._instance._initialize_metrics()
        return cls._instance
    
    def _initialize_metrics(self):
        """Initialize Prometheus metrics."""
        try:
            # Workflow Duration Histogram
            self.workflow_duration = Histogram(
                'maf_workflow_duration_seconds',
                'Time spent executing workflow stages',
                ['workflow_name', 'stage_name']
            )
            
            # Agent Execution Counter
            self.agent_execution_count = Counter(
                'maf_agent_execution_total',
                'Total number of agent executions',
                ['agent_name', 'role']
            )
            
            # Error Counter
            self.error_count = Counter(
                'maf_workflow_errors_total',
                'Total number of workflow errors',
                ['workflow_name', 'error_type']
            )
            
            # Active Workflows Gauge
            self.active_workflows = Gauge(
                'maf_active_workflows',
                'Number of currently executing workflows',
                ['workflow_name']
            )
            
            logger.info("Workflow metrics initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics: {str(e)}")
            # Fallback to no-op if metrics fail (don't crash app)
            self.workflow_duration = None
            self.agent_execution_count = None
            self.error_count = None
            self.active_workflows = None

    @contextmanager
    def track_workflow_stage(self, workflow_name: str, stage_name: str):
        """
        Context manager to track duration of a workflow stage.
        
        Usage:
            with metrics.track_workflow_stage("OLB", "planning"):
                # do work
        """
        if not self.workflow_duration:
            yield
            return
            
        start_time = time.time()
        try:
            self.active_workflows.labels(workflow_name=workflow_name).inc()
            yield
        except Exception as e:
            self.error_count.labels(
                workflow_name=workflow_name, 
                error_type=type(e).__name__
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            self.workflow_duration.labels(
                workflow_name=workflow_name, 
                stage_name=stage_name
            ).observe(duration)
            self.active_workflows.labels(workflow_name=workflow_name).dec()
            
    def record_agent_execution(self, agent_name: str, role: str):
        """Record an agent execution event."""
        if self.agent_execution_count:
            self.agent_execution_count.labels(
                agent_name=agent_name, 
                role=role
            ).inc()

# Global instance
metrics = WorkflowMetrics()
