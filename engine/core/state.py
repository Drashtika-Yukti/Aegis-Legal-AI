from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Chat history
    messages: Annotated[List[BaseMessage], add_messages]
    # The original query (Unmasked)
    original_query: str
    # The masked query for the LLM
    masked_query: str
    # Retrieved document chunks
    documents: List[str]
    # Final answer generated (Masked)
    masked_answer: str
    # Final answer for the user (Unmasked)
    final_answer: str
    # Evaluation scores
    is_relevant: bool
    hallucination_detected: bool
    # Extracted facts
    facts: List[str]
