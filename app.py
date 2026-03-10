"""
FastAPI application for the observable AI chatbot.

This module provides the web API endpoints and integrates all observability components:
- Prometheus metrics for request tracking
- Structured logging for debugging and monitoring
- Error handling with proper metric tracking
"""

import time
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
from prometheus_client.exposition import CONTENT_TYPE_LATEST as PROMETHEUS_CONTENT_TYPE

from metrics import REQUEST_COUNT, ERROR_COUNT, REQUEST_LATENCY, TOKEN_USAGE, MODEL_USAGE
from llm_client import call_llm

# Configure structured logging at application startup
# This ensures all log messages include timestamp, level, and message format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="Observable AI Chatbot",
    description="An AI chatbot with comprehensive observability using Prometheus metrics and structured logging"
)

# Default model to use when none is specified
DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
# Alternative free model for testing
ALTERNATIVE_MODEL = "arcee-ai/trinity-mini:free"


@app.get("/chat")
async def chat_endpoint(
    prompt: str = Query(..., description="The prompt to send to the AI model"),
    model: Optional[str] = Query(None, description="The model to use (defaults to Llama 3.3 70B)")
) -> Dict[str, Any]:
    """
    Chat endpoint that processes user prompts with AI models.
    
    Args:
        prompt (str): User's input prompt/question
        model (Optional[str]): Model ID to use, defaults to Llama 3.3 70B Instruct
        
    Returns:
        Dict[str, Any]: Response containing:
            - response (str): AI-generated response
            - model (str): Model that was used
            - input_tokens (int): Estimated input tokens
            - output_tokens (int): Estimated output tokens
            - latency_seconds (float): Request processing time
            
    Raises:
        HTTPException: When API calls fail or models are unavailable
    """
    # Use default model if none specified
    selected_model = model or DEFAULT_MODEL
    
    # Log the incoming request for observability
    logger.info(f'Request received: "{prompt}"')
    logger.info(f'Model selected: {selected_model}')
    
    # Increment request counter BEFORE processing to track all attempts
    # This ensures even failed requests are counted in our metrics
    REQUEST_COUNT.labels(method='GET', endpoint='/chat').inc()
    
    # Record start time for latency measurement
    start_time = time.time()
    
    try:
        # Call the LLM client - this may raise exceptions
        llm_response = call_llm(prompt, selected_model)
        
        # Calculate request latency in seconds
        latency = time.time() - start_time
        
        # Record token usage metrics
        # Input tokens represent the user's prompt complexity
        TOKEN_USAGE.labels(token_type='input').inc(llm_response['input_tokens'])
        # Output tokens represent the AI's response complexity
        TOKEN_USAGE.labels(token_type='output').inc(llm_response['output_tokens'])
        
        # Record which model was used for usage analytics
        MODEL_USAGE.labels(model_name=selected_model).inc()
        
        # Record request latency for performance monitoring
        REQUEST_LATENCY.labels(method='GET', endpoint='/chat').observe(latency)
        
        # Log successful response with key metrics
        total_tokens = llm_response['input_tokens'] + llm_response['output_tokens']
        logger.info(f'Response returned in {latency:.1f}s | tokens: {total_tokens}')
        
        # Check if response is suspiciously short and log warning
        if len(llm_response['response_text']) < 20:
            logger.warning(f'Short response detected: "{llm_response["response_text"]}"')
        
        return {
            "response": llm_response['response_text'],
            "model": selected_model,
            "input_tokens": llm_response['input_tokens'],
            "output_tokens": llm_response['output_tokens'],
            "latency_seconds": round(latency, 2)
        }
        
    except Exception as e:
        # Calculate latency even for failed requests
        latency = time.time() - start_time
        
        # Increment error counter to track failure rates
        # Error type helps identify common failure patterns
        ERROR_COUNT.labels(
            method='GET', 
            endpoint='/chat', 
            error_type=type(e).__name__
        ).inc()
        
        # Record latency for failed requests too
        REQUEST_LATENCY.labels(method='GET', endpoint='/chat').observe(latency)
        
        # Log the full error for debugging purposes
        logger.error(f'Error processing request: {str(e)}')
        
        # Return user-friendly error response
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process request: {str(e)}"
        )


@app.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint for scraping.
    
    Returns:
        str: Prometheus-formatted metrics data
        
    Note:
        This endpoint allows Prometheus to scrape application metrics
        every 5 seconds as configured in prometheus.yml
    """
    # Generate the latest metrics in Prometheus format
    metrics_data = generate_latest()
    
    # Return with correct content type for Prometheus parsing
    from fastapi import Response
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/")
async def root_endpoint():
    """
    Root endpoint providing basic API information.
    
    Returns:
        Dict[str, str]: Basic API metadata and available endpoints
    """
    return {
        "message": "Observable AI Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "Main chat endpoint with prompt and model parameters",
            "/metrics": "Prometheus metrics endpoint for monitoring",
            "/": "This information endpoint"
        },
        "available_models": [
            DEFAULT_MODEL,
            ALTERNATIVE_MODEL
        ]
    }


@app.get("/health")
async def health_endpoint():
    """
    Health check endpoint for monitoring service status.
    
    Returns:
        Dict[str, str]: Service health status
        
    Note:
        This endpoint can be used by orchestration systems
        to verify the service is running correctly.
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    }
