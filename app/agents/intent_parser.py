from app.config import get_groq_api_key
from app.prompts import INTENT_PARSER_PROMPT
from langchain_groq import ChatGroq

def parse_intent(state):
    """Parses the user's intent from their question, using the schema for context."""
    print("---PARSING INTENT (WITH SCHEMA CONTEXT)---")
    question = state["question"]
    schema = state["schema"]

    # LLM
    llm = ChatGroq(model="llama3-8b-8192", groq_api_key=get_groq_api_key())

    # Prompt
    prompt = INTENT_PARSER_PROMPT.format(
        question=question,
        schema=schema
    )

    # Get intent
    intent = llm.invoke(prompt).content.strip()
    print(f"Intent: {intent}")

    return {"intent": intent}