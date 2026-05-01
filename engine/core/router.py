import json
import os
from typing import Dict, Literal
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Intent(BaseModel):
    category: Literal["GREETING", "LEGAL_QUERY", "DOCUMENT_ACTION", "UNKNOWN"] = Field(description="The primary intent of the user.")
    complexity: Literal["LOW", "HIGH"] = Field(description="Complexity of the query.")
    reasoning: str = Field(description="Brief reasoning for the classification.")

class Router:
    """
    Intelligent router to minimize latency and cost.
    Uses local-first approach for simple classification.
    """
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        self.structured_llm = self.llm.with_structured_output(Intent)

    def route(self, query: str) -> Intent:
        prompt = f"Analyze the following query and classify its intent and complexity: {query}"
        try:
            return self.structured_llm.invoke(prompt)
        except Exception as e:
            return Intent(category="UNKNOWN", complexity="LOW", reasoning=f"Error: {str(e)}")

router = Router()
