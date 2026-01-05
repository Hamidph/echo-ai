
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path("/Users/hamid/Documents/ai-visibility")))

try:
    from backend.app.builders.providers import OpenAIProvider, AnthropicProvider, PerplexityProvider, get_provider, LLMProviderEnum
    
    print("Checking OpenAIProvider constants...")
    print(f"GPT-5.1: {OpenAIProvider.MODEL_GPT5_1}")
    
    print("Checking AnthropicProvider constants...")
    print(f"Claude 4.5: {AnthropicProvider.MODEL_CLAUDE_45_SONNET}")
    
    print("Checking PerplexityProvider constants...")
    print(f"Sonar Pro: {PerplexityProvider.MODEL_SONAR_PRO}")
    
    # Test factory
    print("Testing factory...")
    p1 = get_provider(LLMProviderEnum.OPENAI, "sk-test")
    p2 = get_provider(LLMProviderEnum.ANTHROPIC, "sk-test")
    print("Providers instantiated successfully.")
    
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
