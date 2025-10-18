import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from whoami.embeddings import EmbeddingManager
from whoami.llm_client import OpenRouterClient
from whoami.ui import UIComponents, ChatTab, SkillsTab, TimelineTab
from whoami.constants import (
    APP_TITLE,
    APP_ICON,
    APP_LAYOUT,
    SIDEBAR_STATE,
    SAMPLE_QUESTIONS,
    TAB_CHAT,
    TAB_SKILLS,
    TAB_TIMELINE,
    SESSION_MESSAGES,
    SESSION_CHAT_HISTORY,
    SESSION_SELECTED_SKILL,
    SESSION_SELECTED_COMPANY,
    ERROR_INIT_COMPONENTS,
)


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE,
)

# Apply custom CSS
UIComponents.render_custom_css()


@st.cache_resource
def load_embedding_manager() -> EmbeddingManager:
    """
    Load and cache the embedding manager.

    Returns:
        EmbeddingManager instance or None if initialization fails
    """
    try:
        return EmbeddingManager()
    except Exception as e:
        st.error(f"{ERROR_INIT_COMPONENTS}: {e}")
        return None


@st.cache_resource
def load_llm_client() -> OpenRouterClient:
    """
    Load and cache the LLM client.

    Returns:
        OpenRouterClient instance or None if initialization fails
    """
    try:
        return OpenRouterClient()
    except Exception as e:
        st.error(f"{ERROR_INIT_COMPONENTS}: {e}")
        return None


def initialize_session_state():
    """Initialize all session state variables if they don't exist."""
    if SESSION_MESSAGES not in st.session_state:
        st.session_state[SESSION_MESSAGES] = []
    if SESSION_CHAT_HISTORY not in st.session_state:
        st.session_state[SESSION_CHAT_HISTORY] = []
    if SESSION_SELECTED_SKILL not in st.session_state:
        st.session_state[SESSION_SELECTED_SKILL] = None
    if SESSION_SELECTED_COMPANY not in st.session_state:
        st.session_state[SESSION_SELECTED_COMPANY] = None


def main():
    """Main application entry point."""
    # Render header
    UIComponents.render_header()

    # Create tabs
    tab_chat, tab_skills, tab_timeline = st.tabs([TAB_CHAT, TAB_SKILLS, TAB_TIMELINE])

    # Render sidebar
    UIComponents.render_sidebar(SAMPLE_QUESTIONS)

    # Initialize session state
    initialize_session_state()

    # Load managers
    embedding_manager = load_embedding_manager()
    llm_client = load_llm_client()

    if not embedding_manager or not llm_client:
        st.error(ERROR_INIT_COMPONENTS)
        st.stop()

    # Render tabs
    with tab_chat:
        ChatTab.render(embedding_manager, llm_client)

    with tab_skills:
        SkillsTab.render()

    with tab_timeline:
        TimelineTab.render()

    # Render clear chat button
    UIComponents.render_clear_chat_button()


if __name__ == "__main__":
    main()
