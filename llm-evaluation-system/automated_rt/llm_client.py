import os
import json
import asyncio
import openai
import aiohttp
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

class LLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Get generated responses from LLM using system prompts and user prompts
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            
        Returns:
            str: Response text from LLM
        """
        pass

class OpenAIClient(LLMClient):
    """LLM client using OpenAI API"""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initializing the OpenAI client
        
        Args:
            model_name: OpenAI model name to be used
            api_key: OpenAI API key (If none, get a key from environment variables)
        """
        self.model_name = model_name
        self.client = openai.AsyncOpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Get generated responses using the OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                #temperature=0.7,
                #max_tokens=4000
                max_completion_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return f"エラー: {str(e)}"

class AzureOpenAIClient(LLMClient):
    """LLM client using Azure OpenAI API"""
    
    def __init__(
        self, 
        deployment_name: str, 
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: str = "2023-05-15"
    ):
        """
        Initializing the Azure OpenAI client
        
        Args:
            deployment_name: Azure deployment name
            api_key: Azure OpenAI API key
            api_base: Azure OpenAI API endpoint
            api_version: Azure OpenAI API version
        """
        self.deployment_name = deployment_name
        self.client = openai.AsyncAzureOpenAI(
            api_key=api_key or os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=api_version,
            azure_endpoint=api_base or os.environ.get("AZURE_OPENAI_ENDPOINT")
        )
    
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate responses using Azure OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                #temperature=0.7,
                #max_tokens=4000
                max_completion_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Azure OpenAI API error: {e}")
            return f"エラー: {str(e)}"

class HuggingFaceClient(LLMClient):
    """LLM client using Hugging Face Inference API"""
    
    def __init__(
        self,
        model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        api_key: Optional[str] = None
    ):
        """
        Initializing the Hugging Face client
        
        Args:
            model_name: Model name to use
            api_key: Hugging Face API key (If none, get a key from environment variables)
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("HF_API_KEY")
        self.base_url = f"https://router.huggingface.co/hf-inference/models/{model_name}/v1"
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Get generated responses using the Hugging Face Inference API"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=messages,
                #temperature=0.7,
                #max_tokens=4000
                max_completion_tokens=4000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            return f"エラー: {str(e)}"

class OllamaClient(LLMClient):
    """LLM clients using Ollama"""
    
    def __init__(
        self,
        model_name: str = "llama3",
        api_base: Optional[str] = None
    ):
        """
        Initializing the Ollama client
        
        Args:
            model_name: Model name to use (llama3, llama3:8b, llama3:70b etc.)
            api_base: Base URL of Ollama API (If none, the default localhost:11434 will be used)
        """
        self.model_name = model_name
        self.api_base = api_base or "http://localhost:11434/v1/"
        self.client = openai.AsyncOpenAI(base_url=self.api_base, api_key='dummy_key')

    
    #   Using OpenAI compatible API
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Get generated responses using the OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                #temperature=0.7,
                #max_tokens=4000
                max_completion_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Ollama/OpenAI API error: {e}")
            return f"エラー: {str(e)}"
