from langgraph.graph import StateGraph, END
from termcolor import cprint
from app.graph import AgentState
from app.agents.intent_parser import parse_intent
from app.agents.handle_fallback import handle_fallback
from app.agents.table_selector import select_tables
from app.agents.sql_generator import generate_sql
from app.agents.sql_executor import execute_sql
from app.agents.sql_reflector import reflect_on_error
from app.agents.answer_formatter import format_answer_with_ai, display_direct_answer, LARGE_RESULT_THRESHOLD
from app.config import SCHEMA_PATH

# Conditional logic for the graph
def route_after_intent_parsing(state):
    """Routes to the correct workflow based on user intent."""
    intent = state.get("intent", "").strip().lower()
    if intent == "sql_query":
        return "select_tables"
    return "fallback"

def route_after_sql(state):
    """Decides the next step after SQL execution."""
    if state.get("error") and state.get("retries", 0) < 2:
        return "reflect_on_error"
    if state.get("row_count", 0) > LARGE_RESULT_THRESHOLD:
        return "direct_answer"
    return "format_answer_with_ai"

def run_graph(question: str):
    """Runs the agentic graph"""
    try:
        with open(SCHEMA_PATH, 'r') as f:
            schema = f.read()
    except FileNotFoundError:
        return f"Error: The schema file could not be found at {SCHEMA_PATH}. Please ensure it exists."

    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("parse_intent", parse_intent)
    workflow.add_node("fallback", handle_fallback)
    workflow.add_node("select_tables", select_tables)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("reflect_on_error", reflect_on_error)
    workflow.add_node("format_answer_with_ai", format_answer_with_ai)
    workflow.add_node("direct_answer", display_direct_answer)

    # Build graph
    workflow.set_entry_point("parse_intent")

    # Conditional routing after intent parsing
    workflow.add_conditional_edges(
        "parse_intent",
        route_after_intent_parsing,
        {
            "select_tables": "select_tables",
            "fallback": "fallback"
        }
    )

    # SQL workflow
    workflow.add_edge("select_tables", "generate_sql")
    workflow.add_edge("generate_sql", "execute_sql")
    workflow.add_conditional_edges(
        "execute_sql",
        route_after_sql,
        {
            "reflect_on_error": "reflect_on_error",
            "direct_answer": "direct_answer",
            "format_answer_with_ai": "format_answer_with_ai"
        }
    )
    workflow.add_edge("reflect_on_error", "generate_sql")

    # Endpoints
    workflow.add_edge("fallback", END)
    workflow.add_edge("format_answer_with_ai", END)
    workflow.add_edge("direct_answer", END)

    # Compile
    app = workflow.compile()

    # Run
    inputs = {"question": question, "schema": schema, "retries": 0}
    result = app.invoke(inputs)

    return result['answer']

def main():
    """Main entry point for the application"""
    cprint("Welcome to the MFT Finance AI Assistant!", "blue", attrs=["bold"])
    cprint("Ask a question about your database (or type 'exit' to quit)", "blue")

    while True:
        question = input("> ")
        if question.lower() == 'exit':
            break
        
        answer = run_graph(question)
        cprint(f"\n{answer}\n", "green")

if __name__ == "__main__":
    main()