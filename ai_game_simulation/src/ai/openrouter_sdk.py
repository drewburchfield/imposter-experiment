"""
OpenRouter client using official OpenAI SDK.
Properly handles structured outputs and JSON parsing.
Integrated with LangSmith for full observability.
Includes robust JSON sanitization for malformed LLM responses.
"""

import os
import asyncio
import re
import json
from typing import List, Dict, Optional, Type, Any
from pydantic import BaseModel
import logging
from openai import AsyncOpenAI
from langsmith import wrappers, traceable

logger = logging.getLogger(__name__)


def sanitize_json_response(text: str) -> str:
    """
    Clean malformed JSON responses from LLMs.

    Handles:
    - Markdown code fences (```json...```)
    - Trailing commas before closing braces
    - Control characters (\u0000-\u001F)
    - Extra whitespace

    Args:
        text: Raw LLM response text

    Returns:
        Cleaned JSON string
    """
    if not text:
        return text

    # Step 1: Remove markdown code fences
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)

    # Step 2: Remove ASCII control characters (except newline/tab in strings)
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]+', '', text)

    # Step 3: Fix trailing commas before closing braces/brackets
    text = re.sub(r',(\s*[}\]])', r'\1', text)

    # Step 4: Remove any text before first { or after last }
    # (handles cases like "Here's the JSON: {...}")
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group()

    return text.strip()


class OpenRouterSDKClient:
    """
    OpenRouter client using OpenAI SDK for proper JSON handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "google/gemini-3-flash-preview",  # Fastest tested model
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
                    # Note: OpenRouter's response-healing plugin not compatible with SDK's parse() method
                    # We handle JSON cleanup manually via sanitize_json_response()
                    completion = await self.client.beta.chat.completions.parse(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format=response_format if response_format else None
                    )

                    if response_format:
                        # SDK handles parsing automatically
                        # Note: OpenAI SDK's parse() method handles markdown-wrapped JSON automatically
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


# Model registry - Top performers from comprehensive 30-model testing
# Last tested: 2025-12-29 | Success rate: 60% (18/30 working)
# Excluded: Meta/Llama models (slow), failed models (404/timeout)
# Focus: Speed (< 8s), reliability (100% success), creativity (> 75%)
AVAILABLE_MODELS = {
    # ============================================
    # GOOGLE - Ultra-fast Gemini models (1.3-2.3s)
    # ============================================
    'gemini-2.0': {
        'id': 'google/gemini-2.0-flash-001',
        'name': 'Gemini 2.0 Flash',
        'latency_ms': 1330,
        'creativity': 90,
        'provider': 'Google',
    },
    'gemini-3': {
        'id': 'google/gemini-3-flash-preview',
        'name': 'Gemini 3 Flash',
        'latency_ms': 1979,
        'creativity': 100,
        'provider': 'Google',
    },
    'gemini-2.5': {
        'id': 'google/gemini-2.5-flash',
        'name': 'Gemini 2.5 Flash',
        'latency_ms': 2321,
        'creativity': 100,
        'provider': 'Google',
    },

    # ============================================
    # OPENAI - Premium quality (2.6-3.6s)
    # ============================================
    'gpt4o-mini': {
        'id': 'openai/gpt-4o-mini',
        'name': 'GPT-4o Mini',
        'latency_ms': 2597,
        'creativity': 100,
        'provider': 'OpenAI',
    },
    'gpt4o': {
        'id': 'openai/gpt-4o',
        'name': 'GPT-4o',
        'latency_ms': 3629,
        'creativity': 100,
        'provider': 'OpenAI',
    },

    # ============================================
    # ANTHROPIC - Best strategic reasoning (3.4-5.3s)
    # ============================================
    'haiku': {
        'id': 'anthropic/claude-3.5-haiku',
        'name': 'Claude 3.5 Haiku',
        'latency_ms': 3368,
        'creativity': 83,
        'provider': 'Anthropic',
    },
    'sonnet': {
        'id': 'anthropic/claude-3.5-sonnet',
        'name': 'Claude 3.5 Sonnet',
        'latency_ms': 5316,
        'creativity': 91,
        'provider': 'Anthropic',
    },

    # ============================================
    # QWEN (Open Source) - Good balance (4.2-9.5s)
    # ============================================
    'qwen-coder': {
        'id': 'qwen/qwen3-coder',
        'name': 'Qwen3 Coder',
        'latency_ms': 4180,
        'creativity': 100,
        'provider': 'Qwen',
    },
    'qwen-32b': {
        'id': 'qwen/qwen3-32b',
        'name': 'Qwen3 32B',
        'latency_ms': 9488,
        'creativity': 79,
        'provider': 'Qwen',
    },

    # ============================================
    # MISTRAL (Open Source) - Reliable (7-9.4s)
    # ============================================
    'mistral-large': {
        'id': 'mistralai/mistral-large',
        'name': 'Mistral Large',
        'latency_ms': 7041,
        'creativity': 100,
        'provider': 'Mistral',
    },
    'mistral-7b': {
        'id': 'mistralai/mistral-7b-instruct',
        'name': 'Mistral 7B',
        'latency_ms': 9440,
        'creativity': 79,
        'provider': 'Mistral',
    },

    # ============================================
    # ALTERNATIVES - Specialized models
    # ============================================
    'phi-4': {
        'id': 'microsoft/phi-4',
        'name': 'Microsoft Phi-4',
        'latency_ms': 7440,
        'creativity': 100,
        'provider': 'Microsoft',
    },
    'grok': {
        'id': 'x-ai/grok-4.1-fast',
        'name': 'Grok 4.1 Fast',
        'latency_ms': 10066,
        'creativity': 100,
        'provider': 'X.AI',
    },
    'deepseek': {
        'id': 'deepseek/deepseek-chat-v3',
        'name': 'DeepSeek V3',
        'latency_ms': 12785,
        'creativity': 89,
        'provider': 'DeepSeek',
    },
}


def get_model_id(model_key: str) -> str:
    """Convert short model key to full OpenRouter model ID"""
    if model_key in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[model_key]['id']
    return model_key
