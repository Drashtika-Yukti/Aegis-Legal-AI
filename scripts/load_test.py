import sys
import os
import time
import concurrent.futures
import json
sys.path.append(os.getcwd())

from dotenv import load_dotenv
from core.orchestrator import run_nexus

load_dotenv()

def single_request(q_id, query):
    start = time.time()
    try:
        resp = run_nexus(query, f"load_test_{q_id}")
        elapsed = time.time() - start
        return f"Request {q_id} | Time: {elapsed:.2f}s | Success: {resp['hallucination_check']}"
    except Exception as e:
        return f"Request {q_id} | FAILED: {str(e)}"

def run_load_test():
    print("--- STARTING HARD LOAD AND CONCURRENCY TEST (10 CONCURRENT QUERIES) ---")
    
    # 1. Load some real questions
    with open("data/batch_25_questions.json", "r") as f:
        all_q = json.load(f)
        queries = all_q[:10] # Top 10
    
    start_total = time.time()
    
    # 2. Fire concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(single_request, i, q) for i, q in enumerate(queries)]
        
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
            
    total_elapsed = time.time() - start_total
    print(f"\n--- LOAD TEST COMPLETE ---")
    print(f"Total Time for 10 Concurrent RAG Requests: {total_elapsed:.2f}s")
    print(f"Average Throughput: {10/total_elapsed:.2f} req/sec")

if __name__ == "__main__":
    run_load_test()
