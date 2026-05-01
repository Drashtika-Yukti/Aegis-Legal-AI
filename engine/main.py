"""
Aegis Legal Intelligence Engine - Production API
Handles incoming queries, session management, and orchestrates the AI Agentic flow.
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.orchestrator import run_aegis

app = FastAPI(title="Aegis Legal Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"

@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        response = run_aegis(request.query, request.session_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
