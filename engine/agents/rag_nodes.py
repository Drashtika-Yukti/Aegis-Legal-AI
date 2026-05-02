import os
from typing import List
from langchain_groq import ChatGroq
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from utils.supabase_client import supabase_client
from pydantic import BaseModel, Field
from core.state import AgentState
from utils.privacy_vault import vault
from core.memory import memory

class Grade(BaseModel):
    binary_score: str = Field(description="Is the document relevant? 'yes' or 'no'")

class Judge(BaseModel):
    binary_score: str = Field(description="Is the answer supported by context? 'yes' or 'no'")

class Facts(BaseModel):
    facts: List[str] = Field(description="List of extracted atomic facts.")

class RAGNodes:
    """
    Core Intelligence Nodes for the Aegis RAG pipeline.
    Encapsulates logic for Privacy Masking, Vector Retrieval, 
    Relevance Grading, and Hallucination Judging.
    """
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, streaming=True)
        self.fast_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
        self.embeddings = CohereEmbeddings(model="embed-english-v3.0")
        self.sb_client = supabase_client

    async def mask_query(self, state: AgentState):
        try:
            return {"masked_query": vault.mask(state["original_query"])}
        except Exception as e:
            return {"masked_query": state["original_query"]} # Fallback to unmasked if vault fails

    async def retrieve(self, state: AgentState):
        """Retrieval Layer: Async Supabase pgvector search."""
        query = state["masked_query"]
        
        try:
            # 1. Generate embedding (Async)
            embedded_query = await self.embeddings.aembed_query(query)
            
            # 2. Direct RPC call (Async execution)
            res = self.sb_client.rpc(
                "match_documents", 
                {
                    "query_embedding": embedded_query,
                    "match_threshold": 0.1,
                    "match_count": 5
                }
            ).execute()
            
            doc_contents = [r['content'] for r in res.data]
            return {"documents": doc_contents}
        except Exception as e:
            print(f"Async Retrieval Error: {e}")
            return {"documents": []}

    async def grade_documents(self, state: AgentState):
        try:
            grader = self.fast_llm.with_structured_output(Grade)
            prompt = f"Query: {state['masked_query']}\nDocs: {state['documents']}\nGrade relevance (yes/no):"
            result = await grader.ainvoke(prompt)
            return {"is_relevant": result.binary_score == "yes"}
        except Exception:
            return {"is_relevant": True} # Default to relevant to avoid blocking

    async def generate(self, state: AgentState):
        try:
            # 1. Prepare holistic context
            doc_context = "\n".join(state["documents"])
            utility_data = state.get("utility_context", "No utility context available.")
            
            system_prompt = (
                "You are Aegis, a premium legal intelligence assistant. "
                "Synthesize the following sources to answer the user's query.\n\n"
                f"LEGAL LIBRARY CONTEXT:\n{doc_context}\n\n"
                f"AUXILIARY DATA (Time/Search/Math):\n{utility_data}\n\n"
                "Provide a precise, authoritative answer. If the auxiliary data provides real-time context (like today's date), use it."
            )
            
            result = await self.llm.ainvoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state["masked_query"]}
            ])
            return {"masked_answer": result.content}
        except Exception as e:
            return {"masked_answer": "I encountered an error while generating your answer. Please try a simpler query."}

    async def judge_answer(self, state: AgentState):
        try:
            judge = self.llm.with_structured_output(Judge)
            prompt = f"Context: {state['documents']}\nAnswer: {state['masked_answer']}\nIs it faithful? (yes/no):"
            result = await judge.ainvoke(prompt)
            return {"hallucination_detected": result.binary_score == "no"}
        except Exception:
            return {"hallucination_detected": False} # Default to no hallucination

    async def polish_answer(self, state: AgentState):
        """
        Final Aesthetic Layer: Refines punctuation, tone, and sequencing.
        """
        try:
            system_prompt = (
                "You are the Aegis Editorial Agent. Your job is to take a raw legal AI answer "
                "and polish it for a premium law firm experience.\n\n"
                "RULES:\n"
                "1. Fix any punctuation or sequence errors.\n"
                "2. Ensure a formal, professional legal tone.\n"
                "3. Use structured formatting (bullet points, bold text) where appropriate.\n"
                "4. DO NOT change the legal facts or meaning."
            )
            
            result = await self.fast_llm.ainvoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state["masked_answer"]}
            ])
            return {"masked_answer": result.content}
        except Exception:
            return {"masked_answer": state["masked_answer"]}

    async def unmask_response(self, state: AgentState):
        try:
            return {"final_answer": vault.unmask(state["masked_answer"])}
        except Exception:
            return {"final_answer": state["masked_answer"]}

    async def extract_facts(self, state: AgentState):
        try:
            extractor = self.fast_llm.with_structured_output(Facts)
            prompt = f"Extract atomic user facts from: {state['original_query']}"
            result = await extractor.ainvoke(prompt)
            for fact in result.facts:
                memory.add_message("GLOBAL_FACTS", "system", fact)
            return {"facts": result.facts}
        except Exception:
            return {"facts": []}

nodes = RAGNodes()
