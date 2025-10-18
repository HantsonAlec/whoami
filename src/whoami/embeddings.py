import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from tqdm import tqdm

# Load environment variables
ENV_FILE = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(ENV_FILE)


class EmbeddingManager:
    """Manages document embeddings and vector database operations."""

    # Constants
    DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_DIMENSION = 384
    DEFAULT_BATCH_SIZE = 100
    METADATA_TEXT_LIMIT = 1000

    def __init__(self):
        """
        Initialize the embedding manager.

        Reads configuration from environment variables:
        - PINECONE_API_KEY: Pinecone API key (required)
        - PINECONE_INDEX_NAME: Name of the existing Pinecone index (required)
        - EMBEDDING_MODEL_NAME: HuggingFace model name (optional)
        - EMBEDDING_DIMENSION: Dimension of the embedding vectors (optional)

        Raises:
            ValueError: If required environment variables are missing
        """
        # Load and validate configuration
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")

        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        if not self.index_name:
            raise ValueError("PINECONE_INDEX_NAME not found in environment variables")

        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", self.DEFAULT_MODEL_NAME)
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", str(self.DEFAULT_DIMENSION)))

        # Initialize embedding model
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)

        # Connect to Pinecone
        print(f"Connecting to Pinecone index: {self.index_name}")
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index(self.index_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using SentenceTransformer.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()

    def index_documents(self, chunks: List[Dict], batch_size: int = None):
        """
        Index document chunks into Pinecone vector database.

        Args:
            chunks: List of chunk dictionaries containing 'text' and metadata
            batch_size: Number of vectors to upsert at once (default: 100)
        """
        if batch_size is None:
            batch_size = self.DEFAULT_BATCH_SIZE

        print(f"Indexing {len(chunks)} chunks...")

        vectors = []
        for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
            # Generate embedding
            embedding = self.model.encode(chunk["text"]).tolist()

            # Prepare metadata (Pinecone has size limits)
            metadata = self._prepare_metadata(chunk, i)

            # Create vector tuple (id, embedding, metadata)
            vector_id = f"chunk_{i}"
            vectors.append((vector_id, embedding, metadata))

            # Batch upsert when batch size is reached
            if len(vectors) >= batch_size:
                self.index.upsert(vectors=vectors)
                vectors = []

        # Upsert any remaining vectors
        if vectors:
            self.index.upsert(vectors=vectors)

        print(f"Successfully indexed {len(chunks)} chunks")

    def _prepare_metadata(self, chunk: Dict, index: int) -> Dict:
        """
        Prepare metadata for a chunk, respecting Pinecone size limits.

        Args:
            chunk: Chunk dictionary with text and metadata
            index: Chunk index

        Returns:
            Metadata dictionary
        """
        return {
            "text": chunk["text"][: self.METADATA_TEXT_LIMIT],
            "source": chunk.get("source", "unknown"),
            "doc_type": chunk.get("doc_type", "general"),
            "chunk_index": chunk.get("chunk_index", index),
        }

    def query(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Query the Pinecone index for similar documents.

        Args:
            query_text: Query string
            top_k: Number of results to return

        Returns:
            List of matching chunks with metadata and scores
        """
        # Generate query embedding
        query_embedding = self.model.encode(query_text).tolist()

        # Query Pinecone
        results = self.index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

        # Format results
        formatted_results = []
        for match in results["matches"]:
            formatted_results.append(
                {
                    "text": match["metadata"].get("text", ""),
                    "source": match["metadata"].get("source", "unknown"),
                    "doc_type": match["metadata"].get("doc_type", "general"),
                    "score": match["score"],
                }
            )

        return formatted_results
