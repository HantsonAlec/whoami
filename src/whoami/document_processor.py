import re
from pathlib import Path
from typing import List, Dict
import PyPDF2


class DocumentProcessor:
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        """
        Initialize the document processor.

        Args:
            chunk_size: Target number of words per chunk
            chunk_overlap: Number of words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

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

    def process_document(self, file_path: Path, doc_type: str = None) -> List[Dict]:
        """
        Process a document and return chunked text with metadata.

        Args:
            file_path: Path to the document
            doc_type: Type of document (e.g., 'resume', 'cover_letter')

        Returns:
            List of chunks with metadata
        """
        # Extract text based on file type
        if file_path.suffix.lower() == ".pdf":
            text = self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        # Clean text
        cleaned_text = self.clean_text(text)

        # Create metadata
        metadata = {"source": file_path.name, "doc_type": doc_type or "general", "file_path": str(file_path)}

        # Chunk the text
        chunks = self.chunk_text(cleaned_text, metadata)

        return chunks
