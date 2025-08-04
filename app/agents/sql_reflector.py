from app.config import get_groq_api_key
from app.prompts import SQL_CORRECTOR_PROMPT
from langchain_groq import ChatGroq

def reflect_on_error(state):
    """Reflects on the error and generates a corrected SQL query"""
    print("---REFLECTING ON SQL ERROR---")
    
    # LLM
    llm = ChatGroq(model="llama3-8b-8192", groq_api_key=get_groq_api_key())

    # Prompt
    prompt = SQL_CORRECTOR_PROMPT.format(
        question=state["question"],
        schema=state["schema"],
        sql_query=state["sql_query"],
        error=state["error"]
    )

    # Generate corrected SQL
    corrected_sql = llm.invoke(prompt).content
    print(f"Corrected SQL Query: {corrected_sql}")

    return {"sql_query": corrected_sql, "retries": state["retries"] + 1}
