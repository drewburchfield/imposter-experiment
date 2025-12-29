#!/usr/bin/env python3
"""
Model Health & Quality Testing Framework

Tests 15 diverse models across OpenRouter to:
1. Validate availability (health check)
2. Assess JSON reliability
3. Evaluate clue creativity and quality
4. Measure response latency
5. Determine "fun factor" for gameplay

Usage:
    python test_models.py --quick     # Test with 1 scenario each
    python test_models.py --full      # Test with 5 scenarios each
"""

import asyncio
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai.openrouter_sdk import OpenRouterSDKClient
from src.ai.schemas import ClueResponse, VoteResponse
from src.ai.prompts import build_clue_prompt, build_voting_prompt, PlayerRole

# Load environment
load_dotenv()

# ============================================
# MODEL TEST SUITE (15 diverse models)
# ============================================

TEST_MODELS = {
    # ============================================
    # FRONTIER MODELS (15) - Major Providers
    # ============================================

    # Google (5)
    'gemini-2.5-flash': 'google/gemini-2.5-flash',
    'gemini-2.0-flash': 'google/gemini-2.0-flash-001',
    'gemini-3-flash': 'google/gemini-3-flash-preview',
    'gemini-2.0-exp': 'google/gemini-2.0-flash-exp',
    'gemini-pro': 'google/gemini-pro',

    # Anthropic (3)
    'haiku-3.5': 'anthropic/claude-3.5-haiku',
    'sonnet-3.5': 'anthropic/claude-3.5-sonnet',
    'opus-4.5': 'anthropic/claude-opus-4.5',

    # OpenAI (3)
    'gpt-4o': 'openai/gpt-4o',
    'gpt-4o-mini': 'openai/gpt-4o-mini',
    'gpt-5-mini': 'openai/gpt-5-mini',

    # Meta (3)
    'llama-3.1-8b': 'meta-llama/llama-3.1-8b-instruct',
    'llama-3.1-70b': 'meta-llama/llama-3.1-70b-instruct',
    'llama-3.3-70b': 'meta-llama/llama-3.3-70b-instruct',

    # X.AI (1)
    'grok-fast': 'x-ai/grok-4.1-fast',

    # ============================================
    # ALTERNATIVE/OPEN SOURCE (15) - Other Providers
    # ============================================

    # Qwen (4)
    'qwen-2.5-72b': 'qwen/qwen-2.5-72b-instruct',
    'qwen3-32b': 'qwen/qwen3-32b',
    'qwen3-8b': 'qwen/qwen3-8b',
    'qwen-coder': 'qwen/qwen3-coder',

    # DeepSeek (3)
    'deepseek-v3': 'deepseek/deepseek-chat-v3',
    'deepseek-r1': 'deepseek/deepseek-r1',
    'deepseek-coder': 'deepseek/deepseek-coder',

    # Mistral (3)
    'mistral-7b': 'mistralai/mistral-7b-instruct',
    'mistral-large': 'mistralai/mistral-large',
    'mixtral-8x7b': 'mistralai/mixtral-8x7b-instruct',

    # Others (5)
    'minimax-m2': 'minimax/minimax-01',
    'cohere-command-r': 'cohere/command-r-plus',
    'phi-4': 'microsoft/phi-4',
    'yi-large': 'yi/yi-large',
    'nous-hermes': 'nousresearch/hermes-3-llama-3.1-405b',
}

# ============================================
# TEST SCENARIOS
# ============================================

TEST_SCENARIOS = [
    {
        'word': 'beach',
        'category': 'nature',
        'role': PlayerRole.NON_IMPOSTER,
        'previous_clues': [
            {'round': 1, 'player_id': 'Other_Player', 'clue': 'waves'}
        ]
    },
    {
        'word': 'pizza',
        'category': 'food',
        'role': PlayerRole.NON_IMPOSTER,
        'previous_clues': []
    },
    {
        'word': None,  # Imposter - doesn't know word
        'category': 'sports',
        'role': PlayerRole.IMPOSTER,
        'previous_clues': [
            {'round': 1, 'player_id': 'P1', 'clue': 'orange'},
            {'round': 1, 'player_id': 'P2', 'clue': 'court'}
        ]
    },
    {
        'word': 'mountain',
        'category': 'geography',
        'role': PlayerRole.NON_IMPOSTER,
        'previous_clues': [
            {'round': 1, 'player_id': 'P1', 'clue': 'climbing'},
            {'round': 1, 'player_id': 'P2', 'clue': 'altitude'}
        ]
    },
    {
        'word': None,  # Imposter
        'category': 'animals',
        'role': PlayerRole.IMPOSTER,
        'previous_clues': [
            {'round': 1, 'player_id': 'P1', 'clue': 'stripes'},
            {'round': 1, 'player_id': 'P2', 'clue': 'savanna'},
            {'round': 1, 'player_id': 'P3', 'clue': 'mane'}
        ]
    }
]

# ============================================
# TEST FUNCTIONS
# ============================================

async def test_model_clue_generation(
    client: OpenRouterSDKClient,
    model_id: str,
    scenario: Dict
) -> Dict:
    """
    Test a model's clue generation capability.
    Returns metrics on success, quality, latency, creativity.
    """
    result = {
        'model': model_id,
        'test': 'clue_generation',
        'scenario': f"{scenario['category']} - {scenario['role'].value}",
        'available': False,
        'json_valid': False,
        'latency_ms': None,
        'clue': None,
        'creativity_score': None,
        'error': None
    }

    try:
        # Build prompt
        messages = [{
            'role': 'user',
            'content': build_clue_prompt(
                player_id='TestPlayer',
                role=scenario['role'],
                current_round=2,
                previous_clues=scenario['previous_clues'],
                word=scenario['word'],
                category=scenario['category']
            )
        }]

        # Time the call
        start = time.time()
        response = await client.call(
            messages=messages,
            model=model_id,
            response_format=ClueResponse,
            temperature=0.7,
            max_tokens=500,
            max_retries=1  # Quick test, don't retry
        )
        latency = (time.time() - start) * 1000

        result['available'] = True
        result['json_valid'] = True
        result['latency_ms'] = round(latency, 2)
        result['clue'] = response.clue
        result['thinking_length'] = len(response.thinking)
        result['confidence'] = response.confidence

        # Creativity score: longer thinking = more strategic
        creativity = min(100, (len(response.thinking) / 500) * 100)
        result['creativity_score'] = round(creativity, 2)

    except Exception as e:
        error_str = str(e)
        result['error'] = error_str[:100]  # Truncate long errors

        # Classify error type
        if '404' in error_str:
            result['error_type'] = 'unavailable'
        elif '429' in error_str:
            result['error_type'] = 'rate_limited'
        elif 'json' in error_str.lower():
            result['error_type'] = 'json_parse_error'
            result['available'] = True  # Model works, just bad JSON
        else:
            result['error_type'] = 'unknown'

    return result


async def test_model_voting(
    client: OpenRouterSDKClient,
    model_id: str
) -> Dict:
    """
    Test a model's voting/analysis capability (more complex reasoning).
    """
    result = {
        'model': model_id,
        'test': 'voting',
        'available': False,
        'json_valid': False,
        'latency_ms': None,
        'error': None
    }

    try:
        # Simple voting scenario
        all_clues = [
            {'round': 1, 'player_id': 'P1', 'clue': 'waves'},
            {'round': 1, 'player_id': 'P2', 'clue': 'sandy'},
            {'round': 1, 'player_id': 'P3', 'clue': 'nature'},  # Suspicious
            {'round': 1, 'player_id': 'P4', 'clue': 'salty'},
        ]

        messages = [{
            'role': 'user',
            'content': build_voting_prompt(
                player_id='TestPlayer',
                role=PlayerRole.NON_IMPOSTER,
                all_clues=all_clues,
                num_imposters=1,
                word='beach',
                category='nature'
            )
        }]

        start = time.time()
        response = await client.call(
            messages=messages,
            model=model_id,
            response_format=VoteResponse,
            temperature=0.5,
            max_tokens=800,
            max_retries=1
        )
        latency = (time.time() - start) * 1000

        result['available'] = True
        result['json_valid'] = True
        result['latency_ms'] = round(latency, 2)
        result['votes'] = response.votes
        result['confidence'] = response.confidence
        result['reasoning_quality'] = len(response.thinking)

    except Exception as e:
        error_str = str(e)
        result['error'] = error_str[:100]

        if '404' in error_str:
            result['error_type'] = 'unavailable'
        elif '429' in error_str:
            result['error_type'] = 'rate_limited'
        elif 'json' in error_str.lower():
            result['error_type'] = 'json_parse_error'
            result['available'] = True
        else:
            result['error_type'] = 'unknown'

    return result


async def run_model_tests(quick_mode: bool = False):
    """
    Run comprehensive model testing suite.

    Args:
        quick_mode: If True, test each model with 1 scenario. If False, test all scenarios.
    """
    print("=" * 80)
    print("🧪 IMPOSTER GAME MODEL TESTING FRAMEWORK")
    print("=" * 80)
    print(f"\nMode: {'QUICK' if quick_mode else 'COMPREHENSIVE'}")
    print(f"Models to test: {len(TEST_MODELS)}")
    print(f"Scenarios per model: {1 if quick_mode else len(TEST_SCENARIOS)}")
    print("\n" + "=" * 80 + "\n")

    client = OpenRouterSDKClient(default_model='meta-llama/llama-3.1-8b-instruct')

    all_results = []

    for model_key, model_id in TEST_MODELS.items():
        print(f"\n🔍 Testing: {model_key} ({model_id})")
        print("-" * 80)

        # Test clue generation
        scenarios_to_test = [TEST_SCENARIOS[0]] if quick_mode else TEST_SCENARIOS

        for i, scenario in enumerate(scenarios_to_test, 1):
            print(f"  [{i}/{len(scenarios_to_test)}] Clue test: {scenario['category']} ({scenario['role'].value})...", end=" ")

            result = await test_model_clue_generation(client, model_id, scenario)
            all_results.append(result)

            if result['available'] and result['json_valid']:
                print(f"✅ {result['latency_ms']}ms | Clue: '{result['clue']}' | Creativity: {result['creativity_score']}")
            elif result['available']:
                print(f"⚠️  JSON error: {result['error_type']}")
            else:
                print(f"❌ {result['error_type']}: {result.get('error', 'Unknown')[:50]}")

            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)

        # Test voting (complex reasoning)
        if not quick_mode:
            print(f"  [V] Voting test...", end=" ")
            result = await test_model_voting(client, model_id)
            all_results.append(result)

            if result['available'] and result['json_valid']:
                print(f"✅ {result['latency_ms']}ms | Votes: {result.get('votes', [])} | Confidence: {result.get('confidence', 0)}")
            elif result['available']:
                print(f"⚠️  JSON error: {result['error_type']}")
            else:
                print(f"❌ {result['error_type']}")

        # Delay between models
        await asyncio.sleep(1.0)

    # ============================================
    # GENERATE REPORT
    # ============================================

    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80 + "\n")

    # Categorize by availability
    available = [r for r in all_results if r['available']]
    unavailable = [r for r in all_results if not r['available']]
    json_issues = [r for r in all_results if r['available'] and not r['json_valid']]
    perfect = [r for r in all_results if r['available'] and r['json_valid']]

    print(f"✅ Fully Working: {len(perfect)}/{len(all_results)} ({len(perfect)/len(all_results)*100:.1f}%)")
    print(f"⚠️  JSON Issues: {len(json_issues)}/{len(all_results)}")
    print(f"❌ Unavailable: {len(unavailable)}/{len(all_results)}")

    print("\n" + "-" * 80 + "\n")

    # Tier models by performance
    print("🏆 MODEL TIERS (for Imposter Game)\n")

    # Calculate aggregate scores per model
    model_scores = {}
    for model_key in TEST_MODELS.keys():
        model_results = [r for r in perfect if model_key in r['model']]
        if model_results:
            avg_latency = sum(r['latency_ms'] for r in model_results) / len(model_results)
            avg_creativity = sum(r.get('creativity_score', 0) for r in model_results if 'creativity_score' in r)
            avg_creativity = avg_creativity / len([r for r in model_results if 'creativity_score' in r]) if any('creativity_score' in r for r in model_results) else 0

            model_scores[model_key] = {
                'success_rate': len(model_results) / len([r for r in all_results if model_key in r['model']]) * 100,
                'avg_latency': avg_latency,
                'avg_creativity': avg_creativity,
                'tests_passed': len(model_results)
            }

    # Sort by success rate, then creativity
    sorted_models = sorted(
        model_scores.items(),
        key=lambda x: (x[1]['success_rate'], x[1]['avg_creativity']),
        reverse=True
    )

    print("TIER 1 - ULTRA RELIABLE (100% success, best for production):")
    for model_key, scores in sorted_models:
        if scores['success_rate'] == 100:
            print(f"  ✅ {model_key:15} | {scores['avg_latency']:6.0f}ms | Creativity: {scores['avg_creativity']:.0f}/100")

    print("\nTIER 2 - MOSTLY RELIABLE (some JSON issues):")
    for model_key, scores in sorted_models:
        if 50 < scores['success_rate'] < 100:
            print(f"  ⚠️  {model_key:15} | {scores['avg_latency']:6.0f}ms | Success: {scores['success_rate']:.0f}%")

    print("\nTIER 3 - UNRELIABLE (unavailable or frequent failures):")
    unavailable_models = set(r['model'] for r in unavailable)
    for model_key, model_id in TEST_MODELS.items():
        if model_id in unavailable_models:
            error_type = next((r['error_type'] for r in unavailable if model_id in r['model']), 'unknown')
            print(f"  ❌ {model_key:15} | {error_type}")

    # ============================================
    # RECOMMENDATIONS
    # ============================================

    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80 + "\n")

    tier1_models = [k for k, s in sorted_models if s['success_rate'] == 100]

    print("PRIMARY MODEL SET (for production):")
    print(f"  {', '.join(tier1_models[:3])}")

    print("\nBACKUP MODEL SET (if primary unavailable):")
    if len(tier1_models) > 3:
        print(f"  {', '.join(tier1_models[3:6])}")

    print("\nBEST FOR IMPOSTERS (high creativity):")
    creative_models = sorted(
        [(k, s['avg_creativity']) for k, s in sorted_models if s['success_rate'] == 100],
        key=lambda x: x[1],
        reverse=True
    )[:3]
    for model, creativity in creative_models:
        print(f"  🎭 {model} (creativity: {creativity:.0f}/100)")

    print("\nFASTEST MODELS (low latency):")
    fast_models = sorted(
        [(k, s['avg_latency']) for k, s in sorted_models if s['success_rate'] == 100],
        key=lambda x: x[1]
    )[:3]
    for model, latency in fast_models:
        print(f"  ⚡ {model} ({latency:.0f}ms average)")

    # ============================================
    # SAVE DETAILED RESULTS
    # ============================================

    output_file = Path(__file__).parent / "data" / "model_test_results.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'mode': 'quick' if quick_mode else 'comprehensive',
            'summary': {
                'total_tests': len(all_results),
                'fully_working': len(perfect),
                'json_issues': len(json_issues),
                'unavailable': len(unavailable)
            },
            'model_scores': model_scores,
            'tier1_models': tier1_models,
            'all_results': all_results
        }, f, indent=2)

    print(f"\n📄 Detailed results saved to: {output_file}")
    print("\n" + "=" * 80)
    print("✅ MODEL TESTING COMPLETE")
    print("=" * 80 + "\n")

    return all_results


# ============================================
# CLI
# ============================================

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test OpenRouter models for Imposter Game")
    parser.add_argument('--quick', action='store_true', help='Quick test (1 scenario per model)')
    parser.add_argument('--full', action='store_true', help='Full test (all scenarios)')

    args = parser.parse_args()

    quick_mode = args.quick or not args.full

    await run_model_tests(quick_mode=quick_mode)


if __name__ == '__main__':
    asyncio.run(main())
