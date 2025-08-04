import duckdb
from app.config import DB_PATH

def execute_sql(state):
    """Execute SQL query and handle errors"""
    print("---EXECUTE SQL---")
    sql_query = state["sql_query"]

    try:
        conn = duckdb.connect(DB_PATH, read_only=True)
        result = conn.execute(sql_query).fetchdf()
        conn.close()
        result_str = result.to_string()
        return {"result": result_str, "error": None}
    except Exception as e:
        print(f"SQL Execution Error: {e}")
        return {"result": "", "error": str(e)}
