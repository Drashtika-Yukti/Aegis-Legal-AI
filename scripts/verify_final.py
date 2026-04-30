import sys
import os
sys.path.append(os.getcwd())

from dotenv import load_dotenv
from core.orchestrator import run_nexus

load_dotenv()

def verify():
    q = "What is the official name of this Act and when was it enacted?"
    resp = run_nexus(q, "final_verification")
    print(f"\n[SYSTEM RESPONSE]:\n{resp['answer']}")

if __name__ == "__main__":
    verify()
