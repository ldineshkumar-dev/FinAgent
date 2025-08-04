import streamlit as st
import time
from app.main import run_graph

# --- Page Configuration ---
st.set_page_config(
    page_title="MFT Finance AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Advanced UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* General Styling */
    body {
        font-family: 'Inter', sans-serif;
        color: #EAEAEA;
    }
    .stApp {
        background: linear-gradient(170deg, #0D1117 0%, #1F1F2E 100%);
    }
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 700;
    }
    
    /* Animation for chat messages */
    @keyframes fadeInSlideUp {
        0% {
            opacity: 0;
            transform: translateY(20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Chat Bubbles */
    .chat-bubble {
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 1rem;
        max-width: 80%;
        display: flex;
        align-items: flex-start;
        gap: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        animation: fadeInSlideUp 0.5s ease-out forwards;
    }
    .user-bubble {
        background: linear-gradient(135deg, #0052D4, #4364F7, #6FB1FC);
        color: #FFFFFF;
        margin-left: auto;
        flex-direction: row-reverse;
    }
    .ai-bubble {
        background: #2E2E3A;
        color: #EAEAEA;
        margin-right: auto;
    }
    .chat-icon {
        font-size: 2rem;
        line-height: 1;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }
    .chat-content {
        flex-grow: 1;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(22, 27, 34, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stSidebar"] h1 {
        font-size: 2rem;
        text-align: center;
    }
    
    /* Input Form */
    .st-form-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem 1.5rem 1.5rem 1.5rem;
        background: linear-gradient(180deg, transparent, #0D1117 80%);
        z-index: 100;
    }
    .stTextInput > div > div > input {
        background-color: rgba(46, 46, 58, 0.8);
        color: #EAEAEA;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6FB1FC;
        box-shadow: 0 0 15px rgba(111, 177, 252, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #0052D4, #4364F7);
        color: white;
        border-radius: 15px;
        padding: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(67, 100, 247, 0.5);
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Content ---
with st.sidebar:
    st.title("MFT Finance AI")
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared. How can I help you now?"}]
        st.rerun()

    st.markdown("### How It Works")
    st.info(
        "This AI assistant uses a multi-agent system to understand your question, query the database, and deliver a natural language answer."
    )
    st.markdown("### Example Questions")
    st.code("What was the total revenue last quarter?")
    st.code("Show all transactions for 'marketing'")
    
    st.markdown("---")
    st.markdown("Built with **Gemini & LangGraph**")
    st.markdown("UI by **MFT**")

# --- Main Chat Interface ---
st.title("✨ MFT Finance AI Assistant")
st.caption("Your intelligent, conversational gateway to financial data.")

# Initialize or display welcome screen
if "messages" not in st.session_state or len(st.session_state.messages) <= 1:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you with your financial data today?"}]
    # You can add a more elaborate welcome screen here if desired

# Chat history container
chat_history_container = st.container()

# Display chat messages
with chat_history_container:
    for message in st.session_state.messages:
        role = message["role"]
        bubble_class = "user-bubble" if role == "user" else "ai-bubble"
        icon = "👤" if role == "user" else "🤖"
        
        st.markdown(
            f"""
            <div class="chat-bubble {bubble_class}">
                <div class="chat-icon">{icon}</div>
                <div class="chat-content">{message["content"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- User Input Form (at the bottom) ---
st.markdown('<div class="st-form-container">', unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Ask your question:", 
        key="user_input", 
        placeholder="e.g., What was the total revenue last month?", 
        label_visibility="collapsed"
    )
    submit_button = st.form_submit_button(label="➤ Send")
st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Form Submission ---
if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# If the last message is from the user, get the AI response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    question = st.session_state.messages[-1]["content"]
    
    with st.spinner("The AI agent is thinking..."):
        try:
            answer = run_graph(question)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            error_message = f"Sorry, an error occurred: {str(e)}. Please try rephrasing your question."
            st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    st.rerun()
