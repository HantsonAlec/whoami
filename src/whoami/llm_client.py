import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""

    # Constants
    DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MAX_TOKENS = 500
    DEFAULT_TEMPERATURE = 0.2
    DEFAULT_TIMEOUT = 30
    MAX_HISTORY_MESSAGES = 6

    def __init__(self, model: str = None, prompts_file: Path = None):
        """
        Initialize OpenRouter client.

        Args:
            model: Model identifier (default uses a free model)
            prompts_file: Path to prompts JSON file (default: config/prompts.json)
        """
        self.is_local = os.getenv("IS_LOCAL", "false").lower() == "true"
        self.model = model or self.DEFAULT_MODEL

        # Initialize API credentials
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key and not self.is_local:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Load prompts from config file
        if prompts_file is None:
            config_dir = Path(__file__).parent.parent.parent / "config"
            prompts_file = config_dir / "prompts.json"

        self.prompts = self._load_prompts(prompts_file)

    def _load_prompts(self, prompts_file: Path) -> Dict[str, str]:
        """
        Load prompts from JSON configuration file.

        Args:
            prompts_file: Path to the prompts JSON file

        Returns:
            Dictionary containing prompt templates

        Raises:
            ValueError: If file not found or contains invalid JSON
        """
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

    def chat(
        self, query: str, context_chunks: List[Dict], chat_history: Optional[List[Dict]] = None
    ) -> Dict[str, any]:
        """
        Generate a response with chat history support.

        Args:
            query: User's question
            context_chunks: Retrieved document chunks with text and metadata
            chat_history: Previous conversation messages (optional)

        Returns:
            Dictionary containing:
                - answer: Generated response text
                - model: Model identifier used
                - sources: List of source documents
                - context_chunks: Original context chunks
                - error: Error message if request failed (optional)
        """
        # Return mocked response if IS_LOCAL is true
        if self.is_local:
            return self._create_mock_response(query, context_chunks)

        # Build messages for API request
        messages = self._build_messages(query, context_chunks, chat_history)

        # Create API payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.DEFAULT_MAX_TOKENS,
            "temperature": self.DEFAULT_TEMPERATURE,
        }

        try:
            response = requests.post(self.API_URL, headers=self.headers, json=payload, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            return self._create_success_response(data, context_chunks)

        except requests.exceptions.RequestException as e:
            return self._create_error_response(str(e))

    def _build_messages(
        self, query: str, context_chunks: List[Dict], chat_history: Optional[List[Dict]]
    ) -> List[Dict]:
        """
        Build the messages list for the API request.

        Args:
            query: User's question
            context_chunks: Retrieved document chunks
            chat_history: Previous conversation messages

        Returns:
            List of message dictionaries
        """
        messages = [{"role": "system", "content": self.prompts.get("system_prompt", "")}]

        # Add recent chat history (limit to avoid token overflow)
        if chat_history:
            messages.extend(chat_history[-self.MAX_HISTORY_MESSAGES :])

        # Add current query with context
        context = self.create_prompt(query, context_chunks)
        messages.append({"role": "user", "content": context})

        return messages

    def _create_mock_response(self, query: str, context_chunks: List[Dict]) -> Dict:
        """Create a mocked response for local development."""
        return {
            "answer": f"This is a mocked message for query: {query}",
            "model": self.model,
            "sources": [chunk.get("source") for chunk in context_chunks],
            "context_chunks": context_chunks,
        }

    def _create_success_response(self, api_data: Dict, context_chunks: List[Dict]) -> Dict:
        """Create a successful response dictionary."""
        return {
            "answer": api_data["choices"][0]["message"]["content"],
            "model": self.model,
            "sources": [chunk.get("source") for chunk in context_chunks],
            "context_chunks": context_chunks,
        }

    def _create_error_response(self, error_message: str) -> Dict:
        """Create an error response dictionary."""
        return {
            "answer": f"Error generating response: {error_message}",
            "model": self.model,
            "sources": [],
            "context_chunks": [],
            "error": error_message,
        }
