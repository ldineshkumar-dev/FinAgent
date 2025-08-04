from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    question: str
    schema: str
    sql_query: str
    result: str
    answer: str
    error: Optional[str]
    retries: int
    messages: List[BaseMessage]
