"""
OpenRouter API client for managing concurrent LLM conversations.
Supports multiple models and structured JSON output.
"""

import asyncio
import aiohttp
import os
import json
from typing import List, Dict, Optional, Any, Type
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Async client for OpenRouter API with support for:
    - Concurrent requests (batch calling)
    - Structured JSON output via Pydantic schemas
    - Rate limiting and error handling
    - Multiple model support
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "meta-llama/llama-3.1-8b-instruct",
        max_concurrent: int = 20,
        request_delay: float = 0.05
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")

        self.default_model = default_model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        # Rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.request_delay = request_delay

        logger.info(f"OpenRouter client initialized with default model: {default_model}")

    async def call(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        response_format: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7,
        max_tokens: int = 400
    ) -> Dict[str, Any]:
        """
        Make a single API call to OpenRouter.

        Args:
            messages: Conversation history in OpenAI format
            model: Model to use (defaults to self.default_model)
            response_format: Pydantic model for structured output
            temperature: Sampling temperature (0-2)
            max_tokens: Max tokens in response

        Returns:
            If response_format provided: Validated Pydantic model instance
            Otherwise: Dict with 'content' key
        """
        async with self.semaphore:
            # Small delay to avoid rate limits
            await asyncio.sleep(self.request_delay)

            model = model or self.default_model

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://imposter-experiment.fly.dev",
                "X-Title": "Imposter Mystery AI Game"
            }

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # Add JSON schema if structured output requested
            if response_format:
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_format.__name__,
                        "strict": True,
                        "schema": response_format.model_json_schema()
                    }
                }

            # Make request with retries
            for attempt in range(3):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            self.base_url,
                            headers=headers,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:

                            if response.status == 200:
                                data = await response.json()
                                content = data["choices"][0]["message"]["content"]

                                if response_format:
                                    # Parse and validate with Pydantic
                                    try:
                                        return response_format.model_validate_json(content)
                                    except Exception as e:
                                        logger.error(f"Failed to parse response: {content}")
                                        raise ValueError(f"Invalid JSON from AI: {e}")

                                return {"content": content}

                            elif response.status == 429:  # Rate limit
                                wait_time = 2 ** attempt
                                logger.warning(f"Rate limited, waiting {wait_time}s...")
                                await asyncio.sleep(wait_time)
                                continue

                            else:
                                error_text = await response.text()
                                raise Exception(f"API error {response.status}: {error_text}")

                except asyncio.TimeoutError:
                    if attempt == 2:
                        raise Exception("API call timed out after 3 attempts")
                    logger.warning(f"Timeout, retrying... (attempt {attempt + 1})")
                    await asyncio.sleep(1)

                except Exception as e:
                    if attempt == 2:
                        raise
                    logger.warning(f"Error: {e}, retrying... (attempt {attempt + 1})")
                    await asyncio.sleep(1)

            raise Exception("Failed after 3 attempts")

    async def batch_call(
        self,
        requests: List[Dict[str, Any]],
        response_format: Optional[Type[BaseModel]] = None
    ) -> List[Any]:
        """
        Execute multiple API calls concurrently.
        Used for parallel player actions (all players give clues simultaneously).

        Args:
            requests: List of request dicts, each with 'messages', 'model', etc.
            response_format: Pydantic model for all responses

        Returns:
            List of responses (may include exceptions if calls failed)
        """
        tasks = []
        for req in requests:
            task = self.call(
                messages=req["messages"],
                model=req.get("model", self.default_model),
                response_format=response_format,
                temperature=req.get("temperature", 0.7),
                max_tokens=req.get("max_tokens", 400)
            )
            tasks.append(task)

        # Gather with exceptions to continue even if some fail
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch call {i} failed: {result}")

        return results


# Model registry with pricing info
AVAILABLE_MODELS = {
    'llama': {
        'id': 'meta-llama/llama-3.1-8b-instruct',
        'name': 'Llama 3.1 8B',
        'cost_per_1m': 0.06,
        'speed': 'very_fast',
        'notes': 'Best cost/performance ratio'
    },
    'gemini': {
        'id': 'google/gemini-flash-1.5',
        'name': 'Gemini Flash 1.5',
        'cost_per_1m': 0.075,
        'speed': 'very_fast',
        'notes': 'Excellent reasoning at low cost'
    },
    'haiku': {
        'id': 'anthropic/claude-3-haiku',
        'name': 'Claude 3 Haiku',
        'cost_per_1m': 0.25,
        'speed': 'fast',
        'notes': 'Sophisticated reasoning, best for deception'
    },
    'gpt4-mini': {
        'id': 'openai/gpt-4o-mini',
        'name': 'GPT-4o Mini',
        'cost_per_1m': 0.15,
        'speed': 'fast',
        'notes': 'OpenAI quality at reasonable cost'
    },
    'mistral': {
        'id': 'mistralai/mistral-7b-instruct',
        'name': 'Mistral 7B',
        'cost_per_1m': 0.06,
        'speed': 'very_fast',
        'notes': 'Good alternative to Llama'
    }
}


def get_model_id(model_key: str) -> str:
    """Convert short model key to full OpenRouter model ID"""
    if model_key in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[model_key]['id']
    return model_key  # Assume it's already a full ID
