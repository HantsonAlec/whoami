from pathlib import Path
from dotenv import load_dotenv
from whoami.document_processor import DocumentProcessor
from whoami.embeddings import EmbeddingManager

# Load environment variables
ENV_FILE = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_FILE)


def main():
    """Main indexing function."""
    doc_processor = DocumentProcessor(chunk_size=200, chunk_overlap=30)
    embedding_manager = EmbeddingManager()

    # Define documents to process
    data_dir = Path(__file__).parent.parent / "data"
    documents = [
        {"path": data_dir / "pdfs" / "resume.pdf", "type": "resume"},
        {"path": data_dir / "pdfs" / "cover_letter.pdf", "type": "cover_letter"},
    ]

    all_chunks = []

    for doc in documents:
        doc_path = doc["path"]
        doc_type = doc["type"]

        if not doc_path.exists():
            print(f"Warning: {doc_path} not found, skipping...")
            continue

        print(f"\nProcessing {doc_path.name} ({doc_type})...")

        try:
            chunks = doc_processor.process_document(doc_path, doc_type)
            all_chunks.extend(chunks)
            print(f"Generated {len(chunks)} chunks")
        except Exception as e:
            print(f" Error processing {doc_path.name}: {e}")

    if not all_chunks:
        print("\n No documents were successfully processed!")
        return

    # Index all chunks
    print(f"\n Total chunks to index: {len(all_chunks)}")
    print("\n Indexing documents into Pinecone...")

    try:
        embedding_manager.index_documents(all_chunks)
        print("\n Successfully indexed all documents!")
        stats = embedding_manager.index.describe_index_stats()
        print(f"   Total vectors: {stats['total_vector_count']}")

    except Exception as e:
        print(f"\n Error indexing documents: {e}")

    print("Indexing complete!")


if __name__ == "__main__":
    main()
