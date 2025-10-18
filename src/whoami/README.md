# WhoAmI Source Code Structure

This directory contains the refactored source code for the WhoAmI AI-powered portfolio assistant.

## Module Overview

### `constants.py`

Contains all application-level constants and configuration values, including:

-   Application settings (title, icon, layout)
-   Query settings (top-k, max history)
-   Sample questions
-   Tab names and messages
-   Session state keys

### `ui.py`

Contains all UI rendering components:

-   **UIComponents**: Reusable UI components (header, sidebar, sources, etc.)
-   **ChatTab**: Chat interface rendering and query processing
-   **SkillsTab**: Skills visualization and interaction
-   **TimelineTab**: Career timeline visualization

### `embeddings.py`

Manages document embeddings and vector database operations:

-   **EmbeddingManager**: Handles document indexing and semantic search using Pinecone
-   Generates embeddings using SentenceTransformers
-   Queries vector database for relevant context

### `llm_client.py`

OpenRouter API client for LLM interactions:

-   **OpenRouterClient**: Manages communication with OpenRouter API
-   Handles prompt construction with context
-   Supports chat history for conversational context
-   Includes local mock mode for development

### `document_processor.py`

Document processing utilities:

-   **DocumentProcessor**: Extracts, cleans, and chunks documents
-   Supports PDF, TXT, and MD file formats
-   Creates overlapping chunks for better context retrieval

### `visualizations.py`

Data visualization components:

-   **SkillsVisualization**: Skills categorization and display
-   **TimelineVisualization**: Interactive career and education timeline
-   Question suggestion generation

### `utils.py`

Utility functions:

-   Session state management helpers
-   Text formatting and truncation
-   Environment variable validation
-   Source formatting

## Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Constants Extraction**: All magic strings and configuration values are centralized
3. **Type Hints**: All functions include proper type annotations
4. **Documentation**: Comprehensive docstrings for all classes and functions
5. **Error Handling**: Consistent error handling patterns throughout
6. **Reusability**: UI components are modular and reusable

## Usage Example

```python
from whoami import EmbeddingManager, OpenRouterClient
from whoami.ui import ChatTab, SkillsTab, TimelineTab

# Initialize managers
embedding_manager = EmbeddingManager()
llm_client = OpenRouterClient()

# Use in Streamlit app
ChatTab.render(embedding_manager, llm_client)
```

## Import Structure

The `__init__.py` file provides convenient imports:

```python
from whoami import (
    EmbeddingManager,
    OpenRouterClient,
    DocumentProcessor,
    SkillsVisualization,
    TimelineVisualization,
)
```
