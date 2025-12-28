"""
OpenRouter client using official OpenAI SDK.
Properly handles structured outputs and JSON parsing.
Integrated with LangSmith for full observability.
"""

import os
import asyncio
from typing import List, Dict, Optional, Type, Any
from pydantic import BaseModel
import logging
from openai import AsyncOpenAI
from langsmith import wrappers, traceable

logger = logging.getLogger(__name__)


class OpenRouterSDKClient:
    """
    OpenRouter client using OpenAI SDK for proper JSON handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "meta-llama/llama-3.1-8b-instruct",
        max_concurrent: int = 20
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found")

        self.default_model = default_model

        # Initialize OpenAI client pointing to OpenRouter
        base_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://imposter-experiment.fly.dev",
                "X-Title": "Imposter Mystery AI Game"
            }
        )

        # Wrap client with LangSmith for observability
        self.client = wrappers.wrap_openai(base_client)

        self.semaphore = asyncio.Semaphore(max_concurrent)

    @traceable(name="openrouter_llm_call")
    async def call(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        response_format: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        max_retries: int = 3
    ) -> Any:
        """
        Make API call using OpenAI SDK with retry logic.
        Handles JSON schema properly.
        Traced with LangSmith for full observability.
        """
        async with self.semaphore:
            model = model or self.default_model

            logger.info(f"📤 SDK Call: {model}")

            # Retry loop for transient failures
            last_error = None
            for attempt in range(max_retries):
                try:
                    # Use OpenAI SDK with response_format
                    completion = await self.client.beta.chat.completions.parse(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format=response_format if response_format else None
                    )

                    if response_format:
                        # SDK handles parsing automatically
                        result = completion.choices[0].message.parsed
                        if attempt > 0:
                            logger.info(f"📥 ✅ Success on retry {attempt + 1}: {type(result).__name__}")
                        else:
                            logger.info(f"📥 ✅ Success: {type(result).__name__}")
                        return result
                    else:
                        content = completion.choices[0].message.content
                        logger.info(f"📥 ✅ Success: {len(content)} chars")
                        return {"content": content}

                except Exception as e:
                    last_error = e
                    logger.warning(f"📥 ⚠️  Attempt {attempt + 1}/{max_retries} failed: {e}")

                    # Don't retry on certain errors (invalid model, auth, etc.)
                    error_str = str(e).lower()
                    if any(term in error_str for term in ['not a valid model', 'unauthorized', 'invalid api key']):
                        logger.error(f"📥 ❌ Non-retryable error: {e}")
                        raise

                    # Exponential backoff before retry
                    if attempt < max_retries - 1:
                        backoff = 2 ** attempt
                        logger.info(f"⏳ Waiting {backoff}s before retry...")
                        await asyncio.sleep(backoff)

            # All retries exhausted
            logger.error(f"📥 ❌ All {max_retries} attempts failed: {last_error}")
            raise last_error

    async def batch_call(
        self,
        requests: List[Dict[str, Any]],
        response_format: Optional[Type[BaseModel]] = None
    ) -> List[Any]:
        """Execute multiple calls concurrently"""
        tasks = []
        for req in requests:
            task = self.call(
                messages=req["messages"],
                model=req.get("model", self.default_model),
                response_format=response_format,
                temperature=req.get("temperature", 0.7),
                max_tokens=req.get("max_tokens", 500)
            )
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)


# Model registry - Updated with verified OpenRouter IDs
AVAILABLE_MODELS = {
    'llama': {
        'id': 'meta-llama/llama-3.1-8b-instruct',
        'name': 'Llama 3.1 8B',
        'cost_per_1m': 0.06,
    },
    'haiku': {
        'id': 'anthropic/claude-3.5-haiku',  # Updated to 3.5
        'name': 'Claude 3.5 Haiku',
        'cost_per_1m': 0.80,
    },
    'gemini': {
        'id': 'google/gemini-flash-1.5',
        'name': 'Gemini Flash 1.5',
        'cost_per_1m': 0.075,
    },
    'gemini-2': {
        'id': 'google/gemini-2.0-flash-exp:free',
        'name': 'Gemini 2.0 Flash (Free)',
        'cost_per_1m': 0.00,
    },
    'qwen': {
        'id': 'qwen/qwq-32b:free',
        'name': 'Qwen QwQ 32B (Reasoning)',
        'cost_per_1m': 0.00,
    },
    'gpt4o-mini': {
        'id': 'openai/gpt-4o-mini',
        'name': 'GPT-4o Mini',
        'cost_per_1m': 0.15,
    },
    'mistral': {
        'id': 'mistralai/mistral-7b-instruct',
        'name': 'Mistral 7B',
        'cost_per_1m': 0.06,
    }
}


def get_model_id(model_key: str) -> str:
    """Convert short model key to full OpenRouter model ID"""
    if model_key in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[model_key]['id']
    return model_key
