import os
from dotenv import load_dotenv

load_dotenv()

def get_groq_api_key():
    return os.getenv("GROQ_API_KEY")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'finance_module.duckdb')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db_schema.txt')
