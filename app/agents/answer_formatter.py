from app.config import get_groq_api_key
from app.prompts import ANSWER_FORMATTER_PROMPT
from langchain_groq import ChatGroq
import pandas as pd

# Define a threshold for what is considered a "large" result
LARGE_RESULT_THRESHOLD = 50

def format_answer_with_ai(state):
    """Formats the answer using an LLM for small, qualitative results."""
    print("---FORMATTING ANSWER WITH AI---")
    question = state["question"]
    result_df = state["result"]

    # Convert DataFrame to string for the prompt
    result_str = result_df.to_string()

    # LLM
    llm = ChatGroq(model="llama3-8b-8192", groq_api_key=get_groq_api_key())

    # Prompt
    prompt = ANSWER_FORMATTER_PROMPT.format(question=question, result=result_str)

    # Format answer
    answer = llm.invoke(prompt).content
    print(f"Formatted Answer: {answer}")

    return {"answer": answer}

def display_direct_answer(state):
    """Formats a direct answer for large tabular data, bypassing the LLM."""
    print("---DISPLAYING DIRECT ANSWER---")
    result_df = state["result"]
    row_count = state["row_count"]

    # Convert DataFrame to markdown for display in Streamlit
    table_md = result_df.head(LARGE_RESULT_THRESHOLD).to_markdown(index=False)
    
    answer = (
        f"The query returned {row_count} rows. "
        f"Here are the first {min(row_count, LARGE_RESULT_THRESHOLD)} results:\n\n"
        f"{table_md}"
    )
    
    return {"answer": answer}