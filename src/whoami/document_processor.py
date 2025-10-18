import re
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2


class DocumentProcessor:
    """Processes documents into clean, chunked text suitable for embedding."""

    # Constants
    DEFAULT_CHUNK_SIZE = 400  # words
    DEFAULT_CHUNK_OVERLAP = 50  # words
    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the document processor.

        Args:
            chunk_size: Target number of words per chunk (default: 400)
            chunk_overlap: Number of words to overlap between chunks (default: 50)
        """
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or self.DEFAULT_CHUNK_OVERLAP

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as string
        """
        text = ""
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
        return text

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r"[^\w\s.,!?;:()\-@]", "", text)
        return text.strip()

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of dictionaries containing chunked text and metadata
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_words)

            chunk_data = {"text": chunk_text, "word_count": len(chunk_words), "chunk_index": len(chunks)}

            if metadata:
                chunk_data.update(metadata)

            chunks.append(chunk_data)

            # Break if we've reached the end
            if i + self.chunk_size >= len(words):
                break

        return chunks

    def process_document(self, file_path: Path, doc_type: Optional[str] = None) -> List[Dict]:
        """
        Process a document and return chunked text with metadata.

        Args:
            file_path: Path to the document to process
            doc_type: Type of document (e.g., 'resume', 'cover_letter')

        Returns:
            List of chunk dictionaries with text and metadata

        Raises:
            ValueError: If file type is not supported
        """
        # Validate file extension
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file_path.suffix}. Supported: {self.SUPPORTED_EXTENSIONS}")

        # Extract text based on file type
        text = self._extract_text(file_path)

        # Clean text
        cleaned_text = self.clean_text(text)

        # Create metadata
        metadata = {
            "source": file_path.name,
            "doc_type": doc_type or "general",
            "file_path": str(file_path),
        }

        # Chunk the text
        chunks = self.chunk_text(cleaned_text, metadata)

        return chunks

    def _extract_text(self, file_path: Path) -> str:
        """
        Extract text from a file based on its extension.

        Args:
            file_path: Path to the file

        Returns:
            Extracted text as string
        """
        if file_path.suffix.lower() == ".pdf":
            return self.extract_text_from_pdf(file_path)
        else:  # .txt or .md
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
