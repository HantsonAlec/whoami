import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from whoami.embeddings import EmbeddingManager
from whoami.llm_client import OpenRouterClient
from whoami.visualizations import SkillsVisualization, TimelineVisualization, generate_question_suggestions


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

    tab_chat, tab_skills, tab_timeline = st.tabs(["💬 Chat", "🎯 Skills", "📅 Timeline"])

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
    if "selected_skill" not in st.session_state:
        st.session_state.selected_skill = None
    if "selected_company" not in st.session_state:
        st.session_state.selected_company = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0

    # Load managers
    embedding_manager = load_embedding_manager()
    llm_client = load_llm_client()

    if not embedding_manager or not llm_client:
        st.error("Failed to initialize required components. Please check your configuration.")
        st.stop()

    # ====== TAB 1: CHAT ======
    with tab_chat:
        # Display chat history first
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "sources" in message:
                    display_sources(message["sources"], message.get("context_chunks", []))

        # Chat input - Always at the bottom
        user_input = st.chat_input("Ask me anything about Alec...")

        # Check for pre-selected questions from other tabs or sidebar
        query = None
        if st.session_state.selected_skill:
            query = st.session_state.selected_skill
            st.session_state.selected_skill = None
        elif st.session_state.selected_company:
            query = st.session_state.selected_company
            st.session_state.selected_company = None
        elif "sample_question" in st.session_state:
            query = st.session_state.sample_question
            del st.session_state.sample_question
        elif user_input:
            query = user_input

        # Process query if exists
        if query:
            st.session_state.messages.append({"role": "user", "content": query})

            try:
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

            # Rerun to display the new messages
            st.rerun()

    # ====== TAB 2: SKILLS VISUALIZATION ======
    with tab_skills:
        st.markdown("### Explore Alec's Technical Skills")
        st.markdown("Click on any skill to get suggested questions about it.")

        st.markdown("**Skills by Category** - Click a skill to ask questions about it")
        categories = SkillsVisualization.get_skill_categories()

        for category, skills in categories.items():
            with st.expander(f"**{category}**", expanded=True):
                cols = st.columns(3)
                for idx, skill in enumerate(skills):
                    with cols[idx % 3]:
                        if st.button(f"🔹 {skill}", key=f"skill_{skill}", use_container_width=True):
                            # Generate suggested questions
                            st.session_state["show_skill_suggestions"] = skill

        if "show_skill_suggestions" in st.session_state:
            skill = st.session_state["show_skill_suggestions"]
            st.markdown(f"### 💡 Ask about **{skill}**:")
            suggestions = generate_question_suggestions(skill, "skill")

            for q in suggestions:
                if st.button(q, key=f"suggestion_{q}", use_container_width=True):
                    st.session_state.selected_skill = q
                    del st.session_state["show_skill_suggestions"]
                    st.success("✓ Question sent! Check the 💬 Chat tab for the answer.")
                    st.rerun()

    # ====== TAB 3: TIMELINE VISUALIZATION ======
    with tab_timeline:
        st.markdown("### Alec's Career & Education Journey")
        st.markdown("Explore the timeline and click on any period to learn more.")

        # Timeline visualization
        fig = TimelineVisualization.create_timeline()
        st.plotly_chart(fig, use_container_width=True)

        # Table view
        st.markdown("### 📋 Detailed View")
        timeline_data = TimelineVisualization.create_timeline_table()

        for item in timeline_data:
            with st.expander(f"{item['Type']} | {item['Organization']} - {item['Title']} ({item['Period']})"):
                st.markdown(f"**Period:** {item['Period']}")
                st.markdown(f"**Technologies:** {item['Key Technologies']}")

                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("Ask about this", key=f"timeline_{item['Organization']}", use_container_width=True):
                        question = f"Tell me about Alec's time at {item['Organization']}"
                        st.session_state.selected_company = question
                        st.success("✓ Question sent! Check the 💬 Chat tab for the answer.")
                        st.rerun()

    # Clear chat button
    if st.session_state.messages:
        if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()


if __name__ == "__main__":
    main()
