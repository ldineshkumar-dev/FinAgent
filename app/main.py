from langgraph.graph import StateGraph, END
from termcolor import cprint
from app.graph import AgentState
from app.agents.table_selector import select_tables
from app.agents.sql_generator import generate_sql
from app.agents.sql_executor import execute_sql
from app.agents.answer_formatter import format_answer
from app.config import SCHEMA_PATH

def run_graph(question: str):
    """Runs the agentic graph"""
    try:
        with open(SCHEMA_PATH, 'r') as f:
            schema = f.read()
    except FileNotFoundError:
        return f"Error: The schema file could not be found at {SCHEMA_PATH}. Please ensure it exists."


    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("select_tables", select_tables)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("format_answer", format_answer)

    # Build graph
    workflow.set_entry_point("select_tables")
    workflow.add_edge("select_tables", "generate_sql")
    workflow.add_edge("generate_sql", "execute_sql")
    workflow.add_edge("execute_sql", "format_answer")
    workflow.add_edge("format_answer", END)

    # Compile
    app = workflow.compile()

    # Run
    inputs = {"question": question, "schema": schema}
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
