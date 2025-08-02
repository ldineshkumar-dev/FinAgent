from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    question: str
    schema: str
    sql_query: str
    result: str
    answer: str
    messages: List[BaseMessage]
