"""
OpenRouter LLM client for the observable AI chatbot.

This module handles communication with OpenRouter using the OpenAI SDK.
It focuses solely on making API calls and returns responses without error handling
- error handling is delegated to the calling app.py module.
"""

from openai import OpenAI
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables at module import time
load_dotenv()


def create_openrouter_client() -> OpenAI:
    """
    Create and configure an OpenAI client for OpenRouter API.
    
    Returns:
        OpenAI: Configured OpenAI client pointing to OpenRouter
        
    Note:
        The client is configured to use OpenRouter's base URL and requires
        an OPENROUTER_API_KEY environment variable to be set.
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )


def call_llm(prompt: str, model: str) -> Dict[str, Any]:
    """
    Make a call to the specified LLM model via OpenRouter.
    
    Args:
        prompt (str): The user's input prompt to send to the LLM
        model (str): The model ID to use (e.g., 'meta-llama/llama-3.3-70b-instruct:free')
        
    Returns:
        Dict[str, Any]: Response dictionary containing:
            - response_text (str): The LLM's generated response
            - input_tokens (int): Estimated number of input tokens
            - output_tokens (int): Estimated number of output tokens
            
    Raises:
        ValueError: If API key is not configured
        Exception: Any API-related errors from OpenAI SDK
        
    Note:
        Token estimation is done using word count approximation.
        In production, you'd want to use proper tokenizers like tiktoken.
    """
    # Create client for each request to ensure fresh configuration
    client = create_openrouter_client()
    
    try:
        # Make the API call to OpenRouter
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,  # Reasonable limit for free models
            temperature=0.7   # Balanced creativity vs coherence
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content
        
        # Estimate tokens using word count approximation
        # This is a simple estimation - in production, use proper tokenizers
        input_tokens = len(prompt.split())
        output_tokens = len(response_text.split())
        
        return {
            "response_text": response_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
        
    except Exception as e:
        # Re-raise exceptions to be handled by app.py
        # This allows the FastAPI endpoint to properly log and track errors
        raise e
