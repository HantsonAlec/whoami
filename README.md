# WhoAmI - Conversational Q&A Web App

A conversational AI web application that answers questions about my skills, experience, and background using RAG (Retrieval-Augmented Generation).

My hosted version can be found here: https://whoami-alec.streamlit.app/

## 🚀 Features

-   **Intelligent Document Search**: Uses Pinecone vector database for semantic search
-   **Natural Conversations**: Powered by OpenRouter API with various LLM options
-   **Source Attribution**: Shows which documents were used to answer questions
-   **Easy Setup**: Simple configuration and document indexing process

## 🛠️ Tech Stack

-   **Frontend**: Streamlit
-   **Vector Database**: Pinecone
-   **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
-   **LLM**: OpenRouter API (supports multiple models including free options)
-   **Document Processing**: PyPDF2 for PDF extraction

## 📋 Prerequisites

-   Python 3.12+
-   Poetry (for dependency management)
-   Pinecone account (free tier available)
-   OpenRouter API key (free tier available)

## 🔧 Installation

1. **Clone the repository**

    ```bash
    git clone https://github.com/HantsonAlec/whoami.git
    cd whoami
    ```

2. **Install dependencies**

    This project uses Poetry for dependency management:

    ```bash
    poetry install
    ```

3. **Set up environment variables**

    ```bash
    cp config/.env.example config/.env
    ```

    Edit `config/.env` and add your API keys

4. **Get API Keys**

    - **Pinecone**: Sign up at [pinecone.io](https://www.pinecone.io/) and get your API key
    - **OpenRouter**: Sign up at [openrouter.ai](https://openrouter.ai/) and get your API key

## 📚 Preparing Your Documents

> **Note**: The `data/` folder is not included in the repository. You'll need to create it and add your own documents.

1. **Collect your documents**

    - Resume (PDF)
    - Cover letters
    - Portfolio descriptions
    - Any other relevant documents

2. **Create the data directory and add your documents**

    ```bash
    mkdir -p data/pdfs data/texts
    ```

    Then add your documents:

    ```bash
    # Place PDFs in data/pdfs/
    cp your_resume.pdf data/pdfs/

    # Place text files in data/texts/
    cp your_document.txt data/texts/
    ```

3. **Update the indexing script**

    Edit `index_documents.py` to include your documents:

    ```python
    documents = [
        {
            'path': data_dir / 'pdfs' / 'Alec_Hantson_Resume.pdf',
            'type': 'resume'
        },
        # Add more documents...
    ]
    ```

## 🚀 Usage

### 1. Index Your Documents

First, process and index your documents into Pinecone:

```bash
poetry run python scripts/index_documents.py
```

Or without Poetry:

```bash
python scripts/index_documents.py
```

This will:

-   Extract text from your documents
-   Break them into chunks
-   Generate embeddings
-   Upload to Pinecone

### 2. Run the Web App

Start the Streamlit application:

```bash
poetry run streamlit run app.py
```

Or without Poetry:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 3. Ask Questions!

Try questions like:

-   "What are Alec's technical skills?"
-   "Tell me about Alec's work experience"
-   "What projects has Alec worked on?"
-   "What is Alec's educational background?"

## 🔄 Updating Documents

To add or update documents:

1. Add new files to the `data/` directory
2. Update the `documents` list in `index_documents.py`
3. Run `python index_documents.py` again

---

Built with ❤️ using Streamlit, Pinecone, and OpenRouter
