# Application Settings
APP_TITLE = "Ask Me Anything - Alec Hantson"
APP_ICON = "👨‍💻"
APP_LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Query Settings
DEFAULT_TOP_K = 5  # Number of context chunks to retrieve
MAX_CHAT_HISTORY = 6  # Maximum number of previous messages to include in LLM context

# Sample Questions
SAMPLE_QUESTIONS = [
    "What are Alec's technical skills?",
    "Tell me about Alec's work experience",
    "What projects has Alec worked on?",
    "What is Alec's educational background?",
    "What programming languages does Alec know?",
]

# Tab Names
TAB_CHAT = "💬 Chat"
TAB_SKILLS = "🎯 Skills"
TAB_TIMELINE = "📅 Timeline"

# Messages
ERROR_NO_CONTEXT = "I couldn't find relevant information to answer your question. Please try rephrasing or ask something else!"
ERROR_INIT_EMBEDDING = "Failed to initialize embedding manager"
ERROR_INIT_LLM = "Failed to initialize LLM client"
ERROR_INIT_COMPONENTS = "Failed to initialize required components. Please check your configuration."
ERROR_GENERATING_RESPONSE = "Error generating response"

SUCCESS_QUESTION_SENT = "✓ Question sent! Check the 💬 Chat tab for the answer."

# Session State Keys
SESSION_MESSAGES = "messages"
SESSION_CHAT_HISTORY = "chat_history"
SESSION_SELECTED_SKILL = "selected_skill"
SESSION_SELECTED_COMPANY = "selected_company"
SESSION_SAMPLE_QUESTION = "sample_question"
SESSION_SHOW_SKILL_SUGGESTIONS = "show_skill_suggestions"

# UI Text
ABOUT_TEXT = """
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

CHAT_INPUT_PLACEHOLDER = "Ask me anything about Alec..."
VIEW_SOURCES_LABEL = "📚 View Sources"
SOURCES_HEADER = "**Information retrieved from {count} document(s):**"
EXCERPTS_HEADER = "**Relevant excerpts:**"
EXCERPT_TEMPLATE = "**Excerpt {num}** (relevance: {score:.2%})"
