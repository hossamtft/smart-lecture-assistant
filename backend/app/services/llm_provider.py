"""
LLM Provider Abstraction Layer
Supports Ollama (local), OpenAI, and Anthropic
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from openai import OpenAI
from anthropic import Anthropic

from ..config import settings


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text completion"""
        pass

    @abstractmethod
    def check_health(self) -> bool:
        """Check if the provider is available"""
        pass


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference"""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using Ollama"""
        url = f"{self.base_url}/api/generate"

        # Build the full prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            **kwargs
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")

    def check_health(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


class OpenAIProvider(LLMProvider):
    """OpenAI provider for GPT models"""

    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or settings.openai_api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using OpenAI"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    def check_health(self) -> bool:
        """Check if OpenAI API is available"""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False


class AnthropicProvider(LLMProvider):
    """Anthropic provider for Claude models"""

    def __init__(self, api_key: str = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model
        self.client = Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using Anthropic"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 2048),
                system=system_prompt or "You are a helpful assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")

    def check_health(self) -> bool:
        """Check if Anthropic API is available"""
        try:
            # Make a minimal request to check API availability
            self.client.messages.create(
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get the configured LLM provider
    """
    provider_name = settings.llm_provider.lower()

    if provider_name == "ollama":
        return OllamaProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "anthropic":
        return AnthropicProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")


# Singleton instance (optional, can create new instances as needed)
llm_provider = get_llm_provider()
