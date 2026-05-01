import os
from typing import List
from langchain_groq import ChatGroq
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client, Client
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
    Core Intelligence Nodes for the Nexus RAG pipeline.
    Encapsulates logic for Privacy Masking, Vector Retrieval, 
    Relevance Grading, and Hallucination Judging.
    """
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        self.fast_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        self.embeddings = CohereEmbeddings(model="embed-english-v3.0")
        
        self.sb_client = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        )

    def mask_query(self, state: AgentState):
        return {"masked_query": vault.mask(state["original_query"])}

    def retrieve(self, state: AgentState):
        """Retrieval Layer: Direct Supabase pgvector search (Latency Optimized)."""
        query = state["masked_query"]
        
        # 1. Generate embedding
        embedded_query = self.embeddings.embed_query(query)
        
        # 2. Direct RPC call to match_documents (Bypassing buggy wrappers)
        try:
            res = self.sb_client.rpc(
                "match_documents", 
                {
                    "query_embedding": embedded_query,
                    "match_threshold": 0.1, # Much more lenient for initial testing
                    "match_count": 5
                }
            ).execute()
            
            doc_contents = [r['content'] for r in res.data]
            return {"documents": doc_contents}
        except Exception as e:
            print(f"Retrieval Error: {e}")
            return {"documents": []}

    def grade_documents(self, state: AgentState):
        grader = self.fast_llm.with_structured_output(Grade)
        prompt = f"Query: {state['masked_query']}\nDocs: {state['documents']}\nGrade relevance (yes/no):"
        result = grader.invoke(prompt)
        return {"is_relevant": result.binary_score == "yes"}

    def generate(self, state: AgentState):
        prompt = f"Context: {state['documents']}\n\nAnswer query: {state['masked_query']}"
        result = self.llm.invoke(prompt)
        return {"masked_answer": result.content}

    def judge_answer(self, state: AgentState):
        judge = self.llm.with_structured_output(Judge)
        prompt = f"Context: {state['documents']}\nAnswer: {state['masked_answer']}\nIs it faithful? (yes/no):"
        result = judge.invoke(prompt)
        return {"hallucination_detected": result.binary_score == "no"}

    def unmask_response(self, state: AgentState):
        return {"final_answer": vault.unmask(state["masked_answer"])}

    def extract_facts(self, state: AgentState):
        extractor = self.fast_llm.with_structured_output(Facts)
        prompt = f"Extract atomic user facts from: {state['original_query']}"
        try:
            result = extractor.invoke(prompt)
            for fact in result.facts:
                memory.add_message("GLOBAL_FACTS", "system", fact)
            return {"facts": result.facts}
        except:
            return {"facts": []}

nodes = RAGNodes()
