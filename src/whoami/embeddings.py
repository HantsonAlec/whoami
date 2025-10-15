import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from tqdm import tqdm

ENV_FILE = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(ENV_FILE)


class EmbeddingManager:
    def __init__(self):
        """
        Initialize the embedding manager.

        Reads configuration from environment variables:
        - PINECONE_API_KEY: Pinecone API key (required)
        - PINECONE_INDEX_NAME: Name of the existing Pinecone index (required)
        - EMBEDDING_MODEL_NAME: HuggingFace model name (default: 'sentence-transformers/all-MiniLM-L6-v2')
        - EMBEDDING_DIMENSION: Dimension of the embedding vectors (default: 384)
        """
        # Load configuration from environment
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")

        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        if not self.index_name:
            raise ValueError("PINECONE_INDEX_NAME not found in environment variables")

        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", "384"))

        # Initialize SentenceTransformer model
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)

        # Initialize Pinecone and connect to existing index
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

    def index_documents(self, chunks: List[Dict], batch_size: int = 100):
        """
        Index document chunks into Pinecone.

        Args:
            chunks: List of chunk dictionaries with 'text' and metadata
            batch_size: Number of vectors to upsert at once
        """
        print(f"Indexing {len(chunks)} chunks...")

        # Prepare vectors for indexing
        vectors = []
        for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
            # Generate embedding
            embedding = self.model.encode(chunk["text"]).tolist()

            # Prepare metadata (Pinecone has limits on metadata size)
            metadata = {
                "text": chunk["text"][:1000],  # Limit text size in metadata
                "source": chunk.get("source", "unknown"),
                "doc_type": chunk.get("doc_type", "general"),
                "chunk_index": chunk.get("chunk_index", i),
            }

            # Create vector tuple
            vector_id = f"chunk_{i}"
            vectors.append((vector_id, embedding, metadata))

            # Batch upsert
            if len(vectors) >= batch_size:
                self.index.upsert(vectors=vectors)
                vectors = []

        # Upsert remaining vectors
        if vectors:
            self.index.upsert(vectors=vectors)

        print(f"Successfully indexed {len(chunks)} chunks")

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
