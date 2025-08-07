"""
MFT Finance AI Assistant - Streamlit UI
Efficient single-SLM interface with modern design.
"""
import streamlit as st
import time
import json
from datetime import datetime
import sys
from pathlib import Path

# Add src to path - Windows compatible
import os
src_path = os.path.join(os.path.dirname(__file__), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from main import FinanceAISystem

# Page configuration
st.set_page_config(
    page_title="MFT Finance AI - Efficient Edition",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Global styling */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 25%, #16213e 50%, #0f1a2e 75%, #0a0f1a 100%);
        animation: backgroundShift 10s ease-in-out infinite alternate;
    }
    
    @keyframes backgroundShift {
        0% { background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 25%, #16213e 50%, #0f1a2e 75%, #0a0f1a 100%); }
        100% { background: linear-gradient(135deg, #0a0f1a 0%, #16213e 25%, #1a1a3e 50%, #0f0f23 75%, #1a1a2e 100%); }
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 200% 200%;
        animation: gradientFlow 6s ease-in-out infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .subtitle {
        text-align: center;
        color: #a0a0a0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Chat styling */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }
    
    .message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        animation: fadeInUp 0.3s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: messageGlow 3s ease-in-out infinite alternate;
        color: white;
        margin-left: 2rem;
        text-align: right;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .user-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    @keyframes messageGlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
    
    .assistant-message {
        background: rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        margin-right: 2rem;
        border-left: 4px solid #667eea;
    }
    
    .system-message {
        background: rgba(255, 193, 7, 0.1);
        color: #ffc107;
        border-left: 4px solid #ffc107;
        font-size: 0.9rem;
    }
    
    .error-message {
        background: rgba(220, 53, 69, 0.1);
        color: #dc3545;
        border-left: 4px solid #dc3545;
    }
    
    /* Metrics styling */
    .metrics-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    .metric-box {
        text-align: center;
        padding: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #a0a0a0;
        text-transform: uppercase;
    }
    
    /* SQL display */
    .sql-display {
        background: rgba(0, 0, 0, 0.3);
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #a0a0a0;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        color: white;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: rgba(15, 15, 35, 0.8);
        backdrop-filter: blur(10px);
    }
    
    /* Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-online {
        background: #28a745;
        animation: pulse 2s infinite;
    }
    
    .status-loading {
        background: #ffc107;
        animation: pulse 1s infinite;
    }
    
    .status-error {
        background: #dc3545;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Table Container with Horizontal Scroll */
    .table-container {
        width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        margin: 1rem 0;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.02);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
    }
    
    /* Custom Scrollbar for Table */
    .table-container::-webkit-scrollbar {
        height: 8px;
    }
    
    .table-container::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    .table-container::-webkit-scrollbar-thumb {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
        transition: background 0.3s ease;
    }
    
    .table-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(90deg, #764ba2, #f093fb);
    }
    
    /* Scroll Fade Effects */
    .table-container::before,
    .table-container::after {
        content: '';
        position: absolute;
        top: 0;
        bottom: 0;
        width: 30px;
        pointer-events: none;
        z-index: 2;
        transition: opacity 0.3s ease;
    }
    
    .table-container::before {
        left: 0;
        background: linear-gradient(to right, rgba(15, 15, 35, 0.8), transparent);
        opacity: 0;
    }
    
    .table-container::after {
        right: 0;
        background: linear-gradient(to left, rgba(15, 15, 35, 0.8), transparent);
        opacity: 0;
    }
    
    .table-container.has-scroll::before,
    .table-container.has-scroll::after {
        opacity: 1;
    }
    
    /* Result tables */
    .result-table {
        width: 100%;
        min-width: 600px; /* Minimum width to trigger horizontal scroll */
        border-collapse: collapse;
        background: rgba(255, 255, 255, 0.05);
        margin: 0;
    }
    
    .result-table th {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
        padding: 1rem 0.75rem;
        text-align: left;
        font-weight: 600;
        color: #667eea;
        white-space: nowrap; /* Prevent header text wrapping */
        position: sticky;
        top: 0;
        z-index: 1;
        border-bottom: 2px solid rgba(102, 126, 234, 0.4);
    }
    
    .result-table td {
        padding: 0.75rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        white-space: nowrap; /* Prevent cell content wrapping */
        max-width: 200px; /* Limit cell width for readability */
        overflow: hidden;
        text-overflow: ellipsis;
        transition: all 0.2s ease;
    }
    
    .result-table td:hover {
        background: rgba(102, 126, 234, 0.1);
        max-width: none; /* Expand on hover to show full content */
        white-space: normal;
        word-wrap: break-word;
        z-index: 3;
        position: relative;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .result-table tr:hover {
        background: rgba(255, 255, 255, 0.03);
    }
    
    /* Table Info Badge */
    .table-info {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Column Count Indicator */
    .column-indicator {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(102, 126, 234, 0.8);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.7rem;
        font-weight: 600;
        z-index: 4;
    }
    
    /* Responsive table adjustments */
    @media (max-width: 768px) {
        .result-table {
            min-width: 500px;
        }
        
        .result-table th,
        .result-table td {
            padding: 0.5rem;
            font-size: 0.85rem;
        }
        
        .table-info {
            font-size: 0.75rem;
            padding: 0.25rem 0.6rem;
        }
    }
</style>

<script>
// Enhanced table scroll detection and UX improvements
document.addEventListener('DOMContentLoaded', function() {
    // Function to detect and handle scroll for table containers
    function handleTableScroll() {
        const tableContainers = document.querySelectorAll('.table-container');
        
        tableContainers.forEach(container => {
            // Check if horizontal scroll is available
            const hasScroll = container.scrollWidth > container.clientWidth;
            
            if (hasScroll) {
                container.classList.add('has-scroll');
                
                // Add scroll event listener for fade effects
                container.addEventListener('scroll', function() {
                    const scrollLeft = container.scrollLeft;
                    const maxScroll = container.scrollWidth - container.clientWidth;
                    
                    // Update fade effects based on scroll position
                    const leftFade = container.querySelector('::before');
                    const rightFade = container.querySelector('::after');
                    
                    // Add visual feedback for scrolling
                    if (scrollLeft > 0) {
                        container.style.setProperty('--left-fade-opacity', '1');
                    } else {
                        container.style.setProperty('--left-fade-opacity', '0');
                    }
                    
                    if (scrollLeft < maxScroll) {
                        container.style.setProperty('--right-fade-opacity', '1');
                    } else {
                        container.style.setProperty('--right-fade-opacity', '0');
                    }
                });
            } else {
                container.classList.remove('has-scroll');
            }
        });
    }
    
    // Run on initial load
    handleTableScroll();
    
    // Re-run when new content is added (for Streamlit updates)
    const observer = new MutationObserver(function(mutations) {
        let shouldRecheck = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && 
                        (node.classList.contains('table-container') || 
                         node.querySelector('.table-container'))) {
                        shouldRecheck = true;
                    }
                });
            }
        });
        
        if (shouldRecheck) {
            setTimeout(handleTableScroll, 100);
        }
    });
    
    // Observe the main content area
    const contentArea = document.querySelector('.main');
    if (contentArea) {
        observer.observe(contentArea, {
            childList: true,
            subtree: true
        });
    }
});
</script>
""", unsafe_allow_html=True)

# Initialize session state
if 'system' not in st.session_state:
    st.session_state.system = None
    st.session_state.initialized = False
    st.session_state.messages = []
    st.session_state.system_metrics = {}

def initialize_system():
    """Initialize the AI system"""
    try:
        with st.spinner("🚀 Initializing MFT Finance AI System..."):
            system = FinanceAISystem()
            success = system.initialize()
            
            if success:
                st.session_state.system = system
                st.session_state.initialized = True
                st.success("✅ System initialized successfully!")
                return True
            else:
                st.error("❌ Failed to initialize system")
                return False
    except Exception as e:
        st.error(f"❌ Initialization error: {str(e)}")
        return False

def add_message(role: str, content: str, metadata: dict = None):
    """Add a message to the chat history"""
    message = {
        'role': role,
        'content': content,
        'timestamp': datetime.now().isoformat(),
        'metadata': metadata or {}
    }
    st.session_state.messages.append(message)

def display_message(message: dict):
    """Display a single message"""
    role = message['role']
    content = message['content']
    metadata = message.get('metadata', {})
    
    if role == 'user':
        st.markdown(f'<div class="message user-message">👤 {content}</div>', unsafe_allow_html=True)
    
    elif role == 'assistant':
        st.markdown(f'<div class="message assistant-message">🤖 {content}</div>', unsafe_allow_html=True)
        
        # Show SQL if available
        if 'sql_query' in metadata:
            st.markdown(f'<div class="sql-display">🔍 SQL: {metadata["sql_query"]}</div>', unsafe_allow_html=True)
        
        # Show metrics if available
        if 'metrics' in metadata:
            metrics = metadata['metrics']
            st.markdown(f"""
            <div class="metrics-container">
                <div class="metric-box">
                    <div class="metric-value">{metrics.get('total_time', 0):.2f}s</div>
                    <div class="metric-label">Total Time</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{metrics.get('sql_generation_time', 0):.3f}s</div>
                    <div class="metric-label">SQL Gen</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{metrics.get('query_execution_time', 0):.3f}s</div>
                    <div class="metric-label">Execution</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    elif role == 'system':
        st.markdown(f'<div class="message system-message">⚙️ {content}</div>', unsafe_allow_html=True)
    
    elif role == 'error':
        st.markdown(f'<div class="message error-message">❌ {content}</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🚀 MFT Finance AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Efficient Single-SLM Natural Language to SQL System</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ System Control")
        
        # System status
        if st.session_state.initialized:
            st.markdown('<span class="status-indicator status-online"></span>System Online', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-indicator status-error"></span>System Offline', unsafe_allow_html=True)
        
        # Initialize button
        if not st.session_state.initialized:
            if st.button("🚀 Initialize System", type="primary"):
                initialize_system()
        
        # System actions
        if st.session_state.initialized:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Refresh"):
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.messages = []
                    st.rerun()
            
            # System metrics
            if st.button("📊 Show Status"):
                try:
                    status = st.session_state.system.get_system_status()
                    st.json(status)
                except Exception as e:
                    st.error(f"Error getting status: {e}")
        
        st.markdown("---")
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        example_queries = [
            "How many accounts are there?",
            "What is the average account balance?",
            "Show me all account types",
            "List the top 10 accounts by balance",
            "What financial years are available?"
        ]
        
        for query in example_queries:
            if st.button(f"💬 {query}", key=f"example_{hash(query)}"):
                if st.session_state.initialized:
                    st.session_state.user_input = query
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### ⚡ Performance")
        
        if st.session_state.system and hasattr(st.session_state.system, 'metrics'):
            metrics = st.session_state.system.metrics
            st.metric("Queries Processed", metrics.get('queries_processed', 0))
            st.metric("Avg Response Time", f"{metrics.get('avg_response_time', 0):.2f}s")
    
    # Main chat interface
    if not st.session_state.initialized:
        st.info("👆 Please initialize the system using the sidebar to start asking questions.")
        st.markdown("""
        ### 🌟 What makes this system special?
        
        - **80% Faster**: Single SLM call vs 5 LLM calls
        - **100% Local**: No API dependencies
        - **Smart Search**: Vector embeddings find relevant tables
        - **Cost Effective**: Minimal computational overhead
        - **Lightning Fast**: Sub-second response times
        """)
        return
    
    # Chat history
    if st.session_state.messages:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            display_message(message)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        add_message('assistant', 'Hello! I\'m your MFT Finance AI Assistant. Ask me anything about your financial data!')
        st.rerun()
    
    # User input
    user_input = st.text_input(
        "💬 Your question:",
        placeholder="e.g., How many accounts were created last year?",
        key="user_input_field"
    )
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        if st.button("🚀 Send", type="primary") or (user_input and st.session_state.get('user_input')):
            process_query = user_input or st.session_state.get('user_input', '')
            st.session_state.user_input = ''  # Clear the session state
            
            if process_query.strip():
                # Add user message
                add_message('user', process_query)
                
                # Show processing indicator
                with st.spinner("🤖 Processing your query..."):
                    try:
                        # Process the query
                        result = st.session_state.system.process_query(process_query)
                        
                        if result['success']:
                            # Add successful response
                            add_message('assistant', result['answer'], {
                                'sql_query': result['sql_query'],
                                'metrics': result['metrics'],
                                'row_count': result.get('row_count', 0)
                            })
                        else:
                            # Add error response
                            add_message('error', f"Error: {result['error']}")
                            if 'sql_query' in result:
                                add_message('system', f"Attempted SQL: {result['sql_query']}")
                    
                    except Exception as e:
                        add_message('error', f"Unexpected error: {str(e)}")
                
                st.rerun()
    
    with col2:
        if st.button("🎲 Random"):
            if st.session_state.initialized:
                import random
                example_queries = [
                    "How many accounts are there?",
                    "What is the average account balance?",
                    "Show me all account types",
                    "List the top 10 accounts by balance",
                    "What financial years are available?"
                ]
                random_query = random.choice(example_queries)
                st.session_state.user_input = random_query
                st.rerun()
    
    with col3:
        if st.button("📋 Export"):
            if st.session_state.messages:
                # Export chat history
                export_data = {
                    'messages': st.session_state.messages,
                    'timestamp': datetime.now().isoformat(),
                    'system_info': 'MFT Finance AI - Efficient Edition'
                }
                
                st.download_button(
                    label="💾 Download Chat",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"finance_ai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()
