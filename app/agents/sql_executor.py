import duckdb
from app.config import DB_PATH
import pandas as pd

def execute_sql(state):
    """Execute SQL query and handle errors, returning a DataFrame."""
    print("---EXECUTE SQL---")
    sql_query = state["sql_query"]

    try:
        # Use a 'with' statement to ensure the connection is always closed
        with duckdb.connect(DB_PATH, read_only=True) as conn:
            result_df = conn.execute(sql_query).fetchdf()
        
        row_count = len(result_df)
        if row_count <= 10:
            print(result_df)
        print(f"Query returned {row_count} rows.")

        return {"result": result_df, "row_count": row_count, "error": None}
    except Exception as e:
        print(f"SQL Execution Error: {e}")
        # Return an empty DataFrame on error
        return {"result": pd.DataFrame(), "row_count": 0, "error": str(e)}