import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from whoami.embeddings import EmbeddingManager
from whoami.llm_client import OpenRouterClient


# Page configuration
st.set_page_config(
    page_title="Ask Me Anything - Alec Hantson", page_icon="👨‍💻", layout="wide", initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        font-size: 0.85rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_embedding_manager():
    """Load and cache the embedding manager."""
    try:
        manager = EmbeddingManager()
        return manager
    except Exception as e:
        st.error(f"Failed to initialize embedding manager: {e}")
        return None


@st.cache_resource
def load_llm_client():
    """Load and cache the LLM client."""
    try:
        return OpenRouterClient()
    except Exception as e:
        st.error(f"Failed to initialize LLM client: {e}")
        return None


def display_sources(sources, context_chunks):
    """Display source information in an expandable section."""
    if sources and context_chunks:
        with st.expander("📚 View Sources", expanded=False):
            unique_sources = list(set(sources))
            st.write(f"**Information retrieved from {len(unique_sources)} document(s):**")
            for source in unique_sources:
                st.markdown(f"- `{source}`")

            st.write("**Relevant excerpts:**")
            for i, chunk in enumerate(context_chunks, 1):
                score = chunk.get("score", 0)
                st.markdown(f"**Excerpt {i}** (relevance: {score:.2%})")
                st.markdown(f"> {chunk['text'][:300]}...")
                st.markdown(f"*From: {chunk['source']}*")
                st.markdown("---")


def main():
    # Header
    st.markdown('<div class="main-header">👨‍💻 Ask Me Anything</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Learn about Alec\'s skills, experience, and background</div>',
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.header("About")

        # Profile section
        st.markdown(
            """
        ###
        Welcome! I am 'AI'lec, Alec's AI assistant. I can answer questions about his:
        - 💼 Professional experience
        - 🎓 Education & skills
        - 🚀 Projects & achievements
        - 📝 Background & interests
        
        **How it works:**
        1. Ask a question about Alec
        2. I search the documents for relevant information
        3. I generate a personalized answer
        
        ---
        """
        )

        # Sample questions
        st.header("Sample Questions")
        sample_questions = [
            "What are Alec's technical skills?",
            "Tell me about Alec's work experience",
            "What projects has Alec worked on?",
            "What is Alec's educational background?",
            "What programming languages does Alec know?",
        ]

        for question in sample_questions:
            if st.button(question, key=question, use_container_width=True):
                st.session_state.sample_question = question

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Load managers
    embedding_manager = load_embedding_manager()
    llm_client = load_llm_client()

    if not embedding_manager or not llm_client:
        st.error("Failed to initialize required components. Please check your configuration.")
        st.stop()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                display_sources(message["sources"], message.get("context_chunks", []))

    # Handle sample question
    if "sample_question" in st.session_state:
        query = st.session_state.sample_question
        del st.session_state.sample_question
    else:
        query = st.chat_input("Ask me anything about Alec...")

    # Process query
    if query:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating response..."):
                try:
                    # Retrieve relevant chunks
                    context_chunks = embedding_manager.query(query, top_k=5)

                    if not context_chunks:
                        response_text = "I couldn't find relevant information to answer your question. Please try rephrasing or ask something else!"
                        sources = []
                    else:
                        response = llm_client.chat(
                            query=query, context_chunks=context_chunks, chat_history=st.session_state.chat_history
                        )

                        response_text = response["answer"]
                        sources = response["sources"]

                    # Display response
                    st.markdown(response_text)

                    # Display sources
                    if context_chunks:
                        display_sources(sources, context_chunks)

                    # Save to chat history
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response_text,
                            "sources": sources,
                            "context_chunks": context_chunks,
                        }
                    )

                    # Update chat history for LLM
                    st.session_state.chat_history.append({"role": "user", "content": query})
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})

                except Exception as e:
                    st.error(f"Error generating response: {e}")

    # Clear chat button
    if st.session_state.messages:
        if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()


if __name__ == "__main__":
    main()
