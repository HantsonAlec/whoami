import os
import json
import requests
from pathlib import Path
from typing import List, Dict


class OpenRouterClient:
    def __init__(self, model: str = "meta-llama/llama-3.3-70b-instruct:free", prompts_file: str = None):
        """
        Initialize OpenRouter client.

        Args:
            model: Model identifier (default uses a free model)
            prompts_file: Path to prompts JSON file (default: config/prompts.json)
        """
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        # Load prompts from config file
        if prompts_file is None:
            # Default to config/prompts.json relative to this file
            config_dir = Path(__file__).parent.parent.parent / "config"
            prompts_file = config_dir / "prompts.json"

        self.prompts = self._load_prompts(prompts_file)

    def _load_prompts(self, prompts_file: Path) -> dict:
        """Load prompts from JSON configuration file."""
        try:
            with open(prompts_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Prompts file not found: {prompts_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in prompts file: {e}")

    def create_prompt(self, query: str, context_chunks: List[Dict]) -> str:
        """
        Create a prompt combining the query and retrieved context.

        Args:
            query: User's question
            context_chunks: Retrieved document chunks

        Returns:
            Formatted prompt string
        """
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get("source", "unknown")
            text = chunk.get("text", "")
            context_parts.append(f"[Source {i}: {source}]\n{text}\n")

        context = "\n".join(context_parts)

        # Create the full prompt using template from config
        prompt_template = self.prompts.get("user_prompt_template", "")
        prompt = prompt_template.format(context=context, query=query)

        return prompt

    def chat(self, query: str, context_chunks: List[Dict], chat_history: List[Dict] = None) -> Dict:
        """
        Generate a response with chat history support.

        Args:
            query: User's question
            context_chunks: Retrieved document chunks
            chat_history: Previous conversation messages

        Returns:
            Dictionary with response and metadata
        """
        # Create context from chunks
        context = self.create_prompt(query, context_chunks)

        messages = []
        messages.append({"role": "system", "content": self.prompts.get("system_prompt", "")})

        if chat_history:
            messages.extend(chat_history[-6:])

        messages.append({"role": "user", "content": context})

        payload = {"model": self.model, "messages": messages, "max_tokens": 500, "temperature": 0.2}

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            return {
                "answer": data["choices"][0]["message"]["content"],
                "model": self.model,
                "sources": [chunk.get("source") for chunk in context_chunks],
                "context_chunks": context_chunks,
            }

        except requests.exceptions.RequestException as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "model": self.model,
                "sources": [],
                "context_chunks": [],
                "error": str(e),
            }
