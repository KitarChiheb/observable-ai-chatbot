# Observable AI Chatbot

A production-ready AI chatbot with comprehensive observability using Prometheus metrics, Grafana dashboards, and structured Python logging. This project demonstrates how to implement the three pillars of observability in an AI application.

## What is Observability?

Observability is the ability to understand a system's internal state by examining its external outputs. It goes beyond basic monitoring by providing deep insights into system behavior, performance, and health through three key pillars.

## The Three Pillars of Observability

- **Logs**: Structured, timestamped events that provide detailed context about system operations
- **Metrics**: Quantitative measurements that track system performance and behavior over time  
- **Traces**: Request flow visualization across distributed system components

## Architecture

```
User → FastAPI → OpenRouter LLM
  ↓        ↓         ↓
/metrics → Prometheus → Grafana
```

The chatbot exposes metrics that Prometheus scrapes every 5 seconds, which are then visualized in Grafana dashboards for real-time monitoring.

## Features

- **FastAPI Web Service**: RESTful API with health checks and comprehensive error handling
- **OpenRouter Integration**: Access to multiple free AI models with automatic failover
- **Prometheus Metrics**: Request counting, latency tracking, error monitoring, and token usage
- **Structured Logging**: Timestamped logs with severity levels for debugging and monitoring
- **Docker Compose**: One-command deployment of the complete monitoring stack
- **Grafana Dashboards**: Pre-configured visualizations for system observability

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- OpenRouter API key (free at https://openrouter.ai/keys)

### Setup and Run

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd observable-ai-chatbot
   cp .env.example .env
   ```

2. **Add your OpenRouter API key**
   ```bash
   # Edit .env file and replace with your actual API key
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

3. **Start the complete stack**
   ```bash
   docker-compose up --build
   ```

4. **Access the services**
   - Chatbot API: http://localhost:8000
   - Prometheus UI: http://localhost:9090
   - Grafana Dashboard: http://localhost:3000 (admin/admin)

## API Usage

### Chat Endpoint

**Windows PowerShell:**
```powershell
curl "http://localhost:8000/chat?prompt=What%20is%20machine%20learning?" -UseBasicParsing
```

**Linux/Mac:**
```bash
curl "http://localhost:8000/chat?prompt=What%20is%20machine%20learning?"
```

**Response:**
```json
{
  "response": "Machine learning is a subset of artificial intelligence...",
  "model": "meta-llama/llama-3.3-70b-instruct:free",
  "input_tokens": 5,
  "output_tokens": 42,
  "latency_seconds": 2.1
}
```

### Available Models
- `meta-llama/llama-3.3-70b-instruct:free` (default - may be rate limited)
- `arcee-ai/trinity-mini:free` (recommended for testing)

**Windows PowerShell:**
```powershell
curl "http://localhost:8000/chat?prompt=Hello&model=arcee-ai/trinity-mini:free" -UseBasicParsing
```

**Linux/Mac:**
```bash
curl "http://localhost:8000/chat?prompt=Hello&model=arcee-ai/trinity-mini:free"
```

## Grafana Dashboard Setup

### 1. Connect Grafana to Prometheus

1. Open Grafana at http://localhost:3000
2. Login with admin/admin
3. Go to Configuration → Data Sources → Add data source
4. Select "Prometheus"
5. Set URL to `http://prometheus:9090` (use service name, not localhost)
6. Click "Save & Test"

### 2. Create Dashboard Panels

Create a new dashboard and add these panels with their exact PromQL queries:

#### Panel 1: Requests/sec
- **Title**: Requests per Second
- **Visualization**: Stat or Time series
- **Query**: `rate(chatbot_requests_total[5m])`

#### Panel 2: Error Rate
- **Title**: Error Rate (%)
- **Visualization**: Single stat or gauge
- **Query**: `rate(chatbot_errors_total[5m]) / rate(chatbot_requests_total[5m]) * 100`

#### Panel 3: p95 Latency
- **Title**: 95th Percentile Latency
- **Visualization**: Time series
- **Query**: `histogram_quantile(0.95, rate(chatbot_request_latency_seconds_bucket[5m]))`

#### Panel 4: Total Tokens
- **Title**: Total Tokens Consumed
- **Visualization**: Stat or Time series
- **Query**: `chatbot_tokens_total`

## Monitoring and Observability

### Console Output Example
```
2024-01-15 10:23:45 INFO  Request received: "What is machine learning?"
2024-01-15 10:23:45 INFO  Model selected: meta-llama/llama-3.3-70b-instruct:free
2024-01-15 10:23:47 INFO  Response returned in 2.1s | tokens: 143
```

### Available Metrics

- `chatbot_requests_total`: Total number of chat requests
- `chatbot_errors_total`: Total number of errors encountered
- `chatbot_request_latency_seconds`: Request duration histogram
- `chatbot_tokens_total`: Token usage by type (input/output)
- `chatbot_model_usage_total`: Model usage counts

### Log Levels

- **INFO**: Normal operation (requests, responses, model selection)
- **WARNING**: Suspicious conditions (very short responses)
- **ERROR**: Exceptions and API failures

## Development

### Local Development

**Windows PowerShell:**
```powershell
# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:OPENROUTER_API_KEY="your_key_here"

# Run locally
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Linux/Mac:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENROUTER_API_KEY=your_key_here

# Run locally
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Project Structure
```
observable-ai-chatbot/
├── app.py              # FastAPI application with endpoints and logging
├── metrics.py          # Prometheus metric definitions
├── llm_client.py       # OpenRouter API client
├── prometheus.yml      # Prometheus configuration
├── docker-compose.yml  # Multi-container orchestration
├── Dockerfile          # Container build instructions
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore file
└── README.md          # This documentation
```

## Testing the Project

This is a **backend-only project** designed to teach observability concepts. There is no frontend - just APIs that you can test directly.

### Testing Methods:

1. **Browser Testing:**
   - http://localhost:8000 - API root with documentation
   - http://localhost:8000/docs - Interactive Swagger UI
   - http://localhost:8000/health - Health check endpoint
   - http://localhost:9090 - Prometheus UI
   - http://localhost:3000 - Grafana dashboard

2. **API Testing (shown above):**
   - Use curl commands to test the chat endpoint
   - Check the /metrics endpoint for Prometheus data
   - View logs with `docker-compose logs chatbot`

3. **Error Testing:**
   - Try invalid model names to see error handling
   - Make requests without required parameters
   - Check Grafana error rate panel (will show data when errors occur)

## Production Considerations

- Change default Grafana password in production
- Use proper tokenizers instead of word counting for accurate token metrics
- Implement rate limiting and authentication for the API
- Set up persistent storage for Prometheus and Grafana data
- Configure alerting rules for proactive monitoring

## License

This project is provided for educational purposes to demonstrate observability concepts in AI applications.
