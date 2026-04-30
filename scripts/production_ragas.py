import sys
import os
sys.path.append(os.getcwd())

import json
from dotenv import load_dotenv
from core.orchestrator import run_nexus
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from langchain_groq import ChatGroq
from langchain_cohere import CohereEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

load_dotenv()

def run_ragas():
    print("--- STARTING PRODUCTION RAGAS EVALUATION ---")
    
    question = "What is the official name of this Act and when was it enacted according to the document?"
    ground_truth = "The Act is called the Bharatiya Nyaya Sanhita, 2023, and it was enacted on 25th December, 2023 (Act No. 45 of 2023)."
    
    # 1. Get Real Answer from System
    print(f"System processing: {question}")
    # We need context for RAGAS, so we use the graph directly
    from core.graph import nexus_graph
    result = nexus_graph.invoke({"original_query": question, "messages": []})
    
    answer = result.get("final_answer", "")
    contexts = [result.get("documents", [])] # Ragas expects a list of lists for contexts
    
    # 2. Build Dataset
    data = {
        "question": [question],
        "answer": [answer],
        "contexts": contexts,
        "ground_truth": [ground_truth]
    }
    dataset = Dataset.from_dict(data)
    
    # 3. Evaluate with Groq as Judge
    print("Evaluating with RAGAS metrics (Faithfulness & Relevance)...")
    eval_llm = LangchainLLMWrapper(ChatGroq(model="llama-3.3-70b-versatile", temperature=0))
    eval_embeddings = LangchainEmbeddingsWrapper(CohereEmbeddings(model="embed-english-v3.0"))
    
    try:
        score = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevancy],
            llm=eval_llm,
            embeddings=eval_embeddings
        )
        
        print("\n=== RAGAS SCORES ===")
        print(f"Faithfulness: {score['faithfulness']:.4f}")
        print(f"Answer Relevancy: {score['answer_relevancy']:.4f}")
        
    except Exception as e:
        print(f"RAGAS Error: {e}")

if __name__ == "__main__":
    run_ragas()
