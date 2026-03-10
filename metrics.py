"""
Prometheus metrics definitions for the observable AI chatbot.

This module centralizes all Prometheus metrics to ensure consistent metric naming
and prevent metric definition conflicts across the application.
"""

from prometheus_client import Counter, Histogram

# REQUEST_COUNT - Counter for total requests received
# Counter is used because requests only ever increase and we want to track the cumulative total
REQUEST_COUNT = Counter(
    'chatbot_requests_total',
    'Total number of chat requests received',
    ['method', 'endpoint']
)

# ERROR_COUNT - Counter for total errors encountered
# Counter is used because errors only ever increase and we want to track the cumulative total
ERROR_COUNT = Counter(
    'chatbot_errors_total',
    'Total number of errors encountered during chat requests',
    ['method', 'endpoint', 'error_type']
)

# REQUEST_LATENCY - Histogram for request duration in seconds
# Histogram is used because it allows us to calculate percentiles (p95, p99) and observe distribution
REQUEST_LATENCY = Histogram(
    'chatbot_request_latency_seconds',
    'Time spent processing chat requests in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float('inf')]
)

# TOKEN_USAGE - Counter for total tokens consumed
# Counter is used because token usage only ever increases and we want to track cumulative consumption
TOKEN_USAGE = Counter(
    'chatbot_tokens_total',
    'Total number of tokens consumed (input + output)',
    ['token_type']  # 'input' or 'output'
)

# MODEL_USAGE - Counter with model_name label to track which model was used
# Counter is used because model selections only ever increase and we want to track usage patterns
MODEL_USAGE = Counter(
    'chatbot_model_usage_total',
    'Total number of times each model was used',
    ['model_name']
)
