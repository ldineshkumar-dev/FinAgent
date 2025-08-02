import re
from app.config import get_groq_api_key
from app.prompts import TABLE_SELECTOR_PROMPT
from langchain_groq import ChatGroq

def select_tables(state):
    """Selects the relevant tables from the schema"""
    print("---SELECTING RELEVANT TABLES---")
    question = state["question"]
    full_schema = state["schema"]

    # Use a simpler model for this classification task
    llm = ChatGroq(model="llama3-8b-8192", groq_api_key=get_groq_api_key())

    # Prompt the LLM to get the relevant table names
    prompt = TABLE_SELECTOR_PROMPT.format(question=question, schema=full_schema)
    response = llm.invoke(prompt)
    relevant_tables_str = response.content.strip()
    
    print(f"Relevant tables identified: {relevant_tables_str}")

    # Split the string into a list of table names
    relevant_tables = [table.strip() for table in relevant_tables_str.split(',')]

    # Extract the full CREATE TABLE statements for the relevant tables
    # This is a simple parser, more robust parsing might be needed for complex schemas
    all_create_statements = re.split(r'(?=CREATE TABLE)', full_schema, flags=re.IGNORECASE)
    
    reduced_schema = ""
    for table_name in relevant_tables:
        # Find the corresponding CREATE TABLE statement
        for statement in all_create_statements:
            # Check if the table name is in the statement (case-insensitive)
            if re.search(r'CREATE TABLE\s+`?' + re.escape(table_name) + r'`?', statement, re.IGNORECASE):
                reduced_schema += statement.strip() + "\n\n"
                break
    
    if not reduced_schema:
        print("Warning: No relevant tables found. Using full schema as a fallback.")
        reduced_schema = full_schema

    return {"schema": reduced_schema}
