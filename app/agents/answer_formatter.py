from app.config import get_groq_api_key
from app.prompts import ANSWER_FORMATTER_PROMPT
from langchain_groq import ChatGroq

def format_answer(state):
    """Format the answer"""
    print("---FORMAT ANSWER---")
    question = state["question"]
    result = state["result"]

    # LLM
    llm = ChatGroq(model="llama3-8b-8192", groq_api_key=get_groq_api_key())

    # Prompt
    prompt = ANSWER_FORMATTER_PROMPT.format(question=question, result=result)

    # Format answer
    answer = llm.invoke(prompt).content
    print(f"Formatted Answer: {answer}")

    return {"answer": answer}
