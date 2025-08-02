import duckdb
from app.config import DB_PATH

def execute_sql(state):
    """Execute SQL query"""
    print("---EXECUTE SQL---")
    sql_query = state["sql_query"]

    try:
        conn = duckdb.connect(DB_PATH, read_only=True)
        result = conn.execute(sql_query).fetchdf()
        conn.close()
        result_str = result.to_string()
    except Exception as e:
        result_str = f"Error executing query: {e}"

    print(f"Result: {result_str}")
    return {"result": result_str}
