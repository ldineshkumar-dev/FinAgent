from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage
import pandas as pd

class AgentState(TypedDict):
    question: str
    # The user's intent, classified as "sql_query" or "non_sql_query".
    intent: str
    schema: str
    sql_query: str
    result: pd.DataFrame
    answer: str
    error: Optional[str]
    retries: int
    row_count: int
    messages: List[BaseMessage]
