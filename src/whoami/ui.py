import streamlit as st
from typing import List, Dict, Any
from whoami.visualizations import SkillsVisualization, TimelineVisualization, generate_question_suggestions
from whoami.constants import (
    ABOUT_TEXT,
    CHAT_INPUT_PLACEHOLDER,
    VIEW_SOURCES_LABEL,
    SOURCES_HEADER,
    EXCERPTS_HEADER,
    EXCERPT_TEMPLATE,
    SESSION_MESSAGES,
    SESSION_CHAT_HISTORY,
    SESSION_SELECTED_SKILL,
    SESSION_SELECTED_COMPANY,
    SESSION_SAMPLE_QUESTION,
    SESSION_SHOW_SKILL_SUGGESTIONS,
    DEFAULT_TOP_K,
    ERROR_NO_CONTEXT,
    ERROR_GENERATING_RESPONSE,
    SUCCESS_QUESTION_SENT,
)


class UIComponents:
    """Collection of reusable UI components."""

    @staticmethod
    def render_custom_css():
        """Inject custom CSS styles into the Streamlit app."""
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

    @staticmethod
    def render_header():
        """Render the main application header."""
        st.markdown('<div class="main-header">👨‍💻 Ask Me Anything</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Learn about Alec\'s skills, experience, and background</div>',
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_sidebar(sample_questions: List[str]):
        """
        Render the sidebar with about section and sample questions.

        Args:
            sample_questions: List of sample questions to display
        """
        with st.sidebar:
            st.header("About")
            st.markdown(ABOUT_TEXT)

            st.header("Sample Questions")
            for question in sample_questions:
                if st.button(question, key=question, use_container_width=True):
                    st.session_state[SESSION_SAMPLE_QUESTION] = question

    @staticmethod
    def render_sources(sources: List[str], context_chunks: List[Dict[str, Any]]):
        """
        Display source information in an expandable section.

        Args:
            sources: List of source document names
            context_chunks: List of context chunks with metadata
        """
        if sources and context_chunks:
            with st.expander(VIEW_SOURCES_LABEL, expanded=False):
                unique_sources = list(set(sources))
                st.write(SOURCES_HEADER.format(count=len(unique_sources)))
                for source in unique_sources:
                    st.markdown(f"- `{source}`")

                st.write(EXCERPTS_HEADER)
                for i, chunk in enumerate(context_chunks, 1):
                    score = chunk.get("score", 0)
                    st.markdown(EXCERPT_TEMPLATE.format(num=i, score=score))
                    st.markdown(f"> {chunk['text'][:300]}...")
                    st.markdown(f"*From: {chunk['source']}*")
                    st.markdown("---")

    @staticmethod
    def render_chat_history():
        """Render the chat message history."""
        for message in st.session_state[SESSION_MESSAGES]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "sources" in message:
                    UIComponents.render_sources(message["sources"], message.get("context_chunks", []))

    @staticmethod
    def render_clear_chat_button():
        """Render the clear chat history button in sidebar."""
        if st.session_state[SESSION_MESSAGES]:
            if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state[SESSION_MESSAGES] = []
                st.session_state[SESSION_CHAT_HISTORY] = []
                st.rerun()


class ChatTab:
    """Handles the chat tab UI and logic."""

    @staticmethod
    def render(embedding_manager, llm_client):
        """
        Render the chat interface.

        Args:
            embedding_manager: EmbeddingManager instance for document retrieval
            llm_client: OpenRouterClient instance for generating responses
        """
        # Display chat history
        UIComponents.render_chat_history()

        # Chat input
        user_input = st.chat_input(CHAT_INPUT_PLACEHOLDER)

        # Handle various query sources
        query = ChatTab._get_query_from_sources(user_input)

        # Process query if exists
        if query:
            ChatTab._process_query(query, embedding_manager, llm_client)

    @staticmethod
    def _get_query_from_sources(user_input: str) -> str:
        """
        Get query from various sources (skill click, company click, sample question, or user input).

        Args:
            user_input: Direct user input from chat

        Returns:
            Query string or None
        """
        if st.session_state.get(SESSION_SELECTED_SKILL):
            query = st.session_state[SESSION_SELECTED_SKILL]
            st.session_state[SESSION_SELECTED_SKILL] = None
            return query
        elif st.session_state.get(SESSION_SELECTED_COMPANY):
            query = st.session_state[SESSION_SELECTED_COMPANY]
            st.session_state[SESSION_SELECTED_COMPANY] = None
            return query
        elif st.session_state.get(SESSION_SAMPLE_QUESTION):
            query = st.session_state[SESSION_SAMPLE_QUESTION]
            del st.session_state[SESSION_SAMPLE_QUESTION]
            return query
        elif user_input:
            return user_input
        return None

    @staticmethod
    def _process_query(query: str, embedding_manager, llm_client):
        """
        Process a user query and update chat state.

        Args:
            query: User's question
            embedding_manager: EmbeddingManager instance
            llm_client: OpenRouterClient instance
        """
        # Add user message to history
        st.session_state[SESSION_MESSAGES].append({"role": "user", "content": query})

        try:
            # Retrieve relevant context
            context_chunks = embedding_manager.query(query, top_k=DEFAULT_TOP_K)

            if not context_chunks:
                response_text = ERROR_NO_CONTEXT
                sources = []
            else:
                # Generate response
                response = llm_client.chat(
                    query=query,
                    context_chunks=context_chunks,
                    chat_history=st.session_state[SESSION_CHAT_HISTORY],
                )
                response_text = response["answer"]
                sources = response["sources"]

            # Add assistant message to history
            st.session_state[SESSION_MESSAGES].append(
                {
                    "role": "assistant",
                    "content": response_text,
                    "sources": sources,
                    "context_chunks": context_chunks,
                }
            )

            # Update chat history for LLM context
            st.session_state[SESSION_CHAT_HISTORY].append({"role": "user", "content": query})
            st.session_state[SESSION_CHAT_HISTORY].append({"role": "assistant", "content": response_text})

        except Exception as e:
            st.error(f"{ERROR_GENERATING_RESPONSE}: {e}")

        # Rerun to display the new messages
        st.rerun()


class SkillsTab:
    """Handles the skills visualization tab UI and logic."""

    @staticmethod
    def render():
        """Render the skills exploration interface."""
        st.markdown("### Explore Alec's Technical Skills")
        st.markdown("Click on any skill to get suggested questions about it.")

        st.markdown("**Skills by Category** - Click a skill to ask questions about it")
        categories = SkillsVisualization.get_skill_categories()

        # Render skill categories
        for category, skills in categories.items():
            with st.expander(f"**{category}**", expanded=True):
                cols = st.columns(3)
                for idx, skill in enumerate(skills):
                    with cols[idx % 3]:
                        if st.button(f"🔹 {skill}", key=f"skill_{skill}", use_container_width=True):
                            st.session_state[SESSION_SHOW_SKILL_SUGGESTIONS] = skill

        # Show suggestions if a skill was clicked
        SkillsTab._render_skill_suggestions()

    @staticmethod
    def _render_skill_suggestions():
        """Render question suggestions for a selected skill."""
        if SESSION_SHOW_SKILL_SUGGESTIONS in st.session_state:
            skill = st.session_state[SESSION_SHOW_SKILL_SUGGESTIONS]
            st.markdown(f"### 💡 Ask about **{skill}**:")
            suggestions = generate_question_suggestions(skill, "skill")

            for q in suggestions:
                if st.button(q, key=f"suggestion_{q}", use_container_width=True):
                    st.session_state[SESSION_SELECTED_SKILL] = q
                    del st.session_state[SESSION_SHOW_SKILL_SUGGESTIONS]
                    st.success(SUCCESS_QUESTION_SENT)
                    st.rerun()


class TimelineTab:
    """Handles the timeline visualization tab UI and logic."""

    @staticmethod
    def render():
        """Render the career and education timeline interface."""
        st.markdown("### Alec's Career & Education Journey")
        st.markdown("Explore the timeline and click on any period to learn more.")

        # Timeline visualization
        fig = TimelineVisualization.create_timeline()
        st.plotly_chart(fig, use_container_width=True)

        # Detailed table view
        TimelineTab._render_detailed_view()

    @staticmethod
    def _render_detailed_view():
        """Render the detailed table view of timeline events."""
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
                        st.session_state[SESSION_SELECTED_COMPANY] = question
                        st.success(SUCCESS_QUESTION_SENT)
                        st.rerun()
