from prometheus_client import Counter, Gauge, start_http_server
import logging

logger = logging.getLogger(__name__)

class MetricsService:
    """
    Centralized service for Prometheus metrics.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsService, cls).__new__(cls)
            cls._instance._initialize_metrics()
        return cls._instance

    def _initialize_metrics(self):
        # Counters
        self.agent_actions_total = Counter(
            'maf_agent_actions_total', 
            'Total number of actions taken by agents',
            ['agent_name', 'action_type']
        )
        self.agent_errors_total = Counter(
            'maf_agent_errors_total',
            'Total number of errors encountered by agents',
            ['agent_name', 'error_type']
        )
        self.decisions_stored_total = Counter(
            'maf_governance_decisions_total',
            'Total number of governance decisions stored',
            ['category']
        )
        
        # Gauges
        self.active_workflows = Gauge(
            'maf_active_workflows',
            'Number of currently active workflows'
        )

    def start_server(self, port: int = 8001):
        """Start the Prometheus metrics server."""
        try:
            start_http_server(port)
            logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")

    # Helper methods to record metrics
    def record_action(self, agent_name: str, action_type: str):
        self.agent_actions_total.labels(agent_name=agent_name, action_type=action_type).inc()

    def record_error(self, agent_name: str, error_type: str):
        self.agent_errors_total.labels(agent_name=agent_name, error_type=error_type).inc()

    def record_decision(self, category: str):
        self.decisions_stored_total.labels(category=category).inc()
