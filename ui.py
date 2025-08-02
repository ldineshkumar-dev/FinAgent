import streamlit as st
from app.main import run_graph

# --- Page Configuration ---
st.set_page_config(
    page_title="MFT Finance AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Dark Theme ---
st.markdown("""
<style>
    /* General Styling */
    body {
        color: #E0E0E0;
    }
    .stApp {
        background-color: #121212;
    }
    h1, h3, .st-emotion-cache-10trblm, .st-emotion-cache-16idsys p {
        color: #FFFFFF;
    }
    .st-emotion-cache-16idsys {
        color: #A0A0A0;
    }
    /* Chat Bubbles */
    .chat-bubble {
        padding: 18px;
        border-radius: 20px;
        margin-bottom: 12px;
        max-width: 85%;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        border: 1px solid transparent;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .user-bubble {
        background: linear-gradient(135deg, #0052D4, #4364F7, #6FB1FC);
        color: #FFFFFF;
        margin-left: auto;
        flex-direction: row-reverse;
        border-color: #4364F7;
    }
    .ai-bubble {
        background-color: #2E2E2E;
        color: #E0E0E0;
        margin-right: auto;
        border-color: #444444;
    }
    .chat-icon {
        font-size: 1.8rem;
        line-height: 1.2;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A;
        border-right: 1px solid #333333;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] .st-emotion-cache-1gulkj5 {
        color: #FAFAFA;
    }
    /* Input Form */
    [data-testid="stForm"] {
        border-top: 1px solid #333333;
        padding-top: 25px;
        background-color: #1A1A1A;
    }
    .st-emotion-cache-1pflw40 {
        background-color: #2E2E2E;
        color: #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("MFT Finance AI")
    st.markdown("---")
    st.markdown("### How to Use")
    st.info(
        "1. **Ask a question:** Type your financial question in the chat box below.\n"
        "2. **Get an answer:** The AI agent will query the database and provide a natural language response.\n"
        "3. **Example:** 'What was the total revenue in the last quarter?'"
    )
    st.markdown("---")
    st.markdown("Built with Gemini & LangGraph")


# --- Main Chat Interface ---
st.title("🤖 MFT Finance AI Assistant")
st.caption("Your intelligent interface to the finance database.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]

# Display chat messages from history
for message in st.session_state.messages:
    role = message["role"]
    bubble_class = "user-bubble" if role == "user" else "ai-bubble"
    icon = "👤" if role == "user" else "🤖"
    
    with st.container():
        st.markdown(
            f'<div class="chat-bubble {bubble_class}>'
            f'<div class="chat-icon">{icon}</div>'
            f'<div>{message["content"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

# --- User Input Form ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask your question:", key="user_input", placeholder="Type your message...", label_visibility="collapsed")
    submit_button = st.form_submit_button(label="Send")

if submit_button and user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Rerun to display the new user message immediately
    st.rerun()

# If the last message is from the user, get the AI response
if st.session_state.messages[-1]["role"] == "user":
    question = st.session_state.messages[-1]["content"]
    
    with st.spinner("The AI agent is thinking..."):
        try:
            answer = run_graph(question)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # Rerun to display the new AI message
    st.rerun()
