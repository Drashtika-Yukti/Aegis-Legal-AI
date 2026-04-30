import sys
import os
sys.path.append(os.getcwd())

import json
from dotenv import load_dotenv
from core.orchestrator import run_nexus

load_dotenv()

def run_final_test():
    print("--- FINAL MULTI-CHUNK STRESS TEST (LANGSMITH TRACING) ---")
    
    # 3 Questions: Simple -> Medium -> Complex (Multi-Chunk)
    questions = [
        "What is the effective date or period covered by this legal document?", # Simple Fact
        "What are the specific procedural requirements mentioned for a petitioner, and how do they relate to the filing fee?", # Medium (Needs 2 facts)
        "Based on the jurisdictional rules and the procedural requirements in this document, summarize the step-by-step process for filing a case in the High Court." # Complex (Synthesis)
    ]
    
    session_id = "final_langsmith_validation"
    
    for i, q in enumerate(questions):
        print(f"\n[PHASE {i+1}] Query: {q}")
        try:
            # This triggers the full production-grade Agentic Flow in Supabase
            resp = run_nexus(q, session_id)
            print(f"[ASSISTANT]: {resp['answer'][:200]}...")
        except Exception as e:
            print(f"[ERROR]: {e}")

    print("\n--- TEST COMPLETE. CHECK LANGSMITH FOR DEEP TRACE ---")

if __name__ == "__main__":
    run_final_test()
