"""
WhoAmI - AI-Powered Portfolio Assistant

A Streamlit application that uses RAG (Retrieval-Augmented Generation)
to answer questions about Alec Hantson's professional background.
"""

from .embeddings import EmbeddingManager
from .llm_client import OpenRouterClient
from .document_processor import DocumentProcessor
from .visualizations import SkillsVisualization, TimelineVisualization

__version__ = "1.0.0"
__all__ = [
    "EmbeddingManager",
    "OpenRouterClient",
    "DocumentProcessor",
    "SkillsVisualization",
    "TimelineVisualization",
]
