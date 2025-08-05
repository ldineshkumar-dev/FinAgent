from app.config import get_groq_api_key
from app.prompts import DEFAULT_SQL_PROMPT
from langchain_groq import ChatGroq

def generate_sql(state):
    """Generate SQL query"""
    print("---GENERATE SQL---")
    question = state["question"]
    schema = state["schema"]

    # LLM
    llm = ChatGroq(model="llama3-8b-8192", groq_api_key=get_groq_api_key())

    # Prompt
    prompt = DEFAULT_SQL_PROMPT.format(question=question, schema=schema)

    # Generate SQL
    sql_query = llm.invoke(prompt).content
    print(f"SQL Query: {sql_query}")

    return {"sql_query": sql_query}
