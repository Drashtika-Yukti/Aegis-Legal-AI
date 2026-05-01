from core.router import router
from core.memory import memory
from core.graph import nexus_graph
from langchain_core.messages import HumanMessage
from core.logger import get_logger

logger = get_logger("AegisEngine")

def run_aegis(query: str, session_id: str = "default"):
    """
    Aegis Master Entry Point.
    """
    logger.info(f"Session {session_id} | Processing query.")

    # 1. Routing
    intent_result = router.route(query)
    
    if intent_result.category == "GREETING":
        return {
            "answer": "Hello! I am Aegis, your Legal Intelligence Assistant. How can I help you today?", 
            "intent": "GREETING",
            "hallucination_check": True
        }

    # 2. Agentic reasoning
    try:
        history = memory.get_history(session_id)
        chat_messages = [HumanMessage(content=msg["content"]) for msg in history]

        result = nexus_graph.invoke({
            "original_query": query,
            "messages": chat_messages
        })

        # 3. Persistence & Fallback
        final_ans = result.get("final_answer", "I am sorry, but I could not find relevant legal information in the current document to answer your request accurately.")
        
        memory.add_message(session_id, "user", query)
        memory.add_message(session_id, "assistant", final_ans)

        return {
            "answer": final_ans,
            "intent": intent_result.category,
            "hallucination_check": not result.get("hallucination_detected", False),
            "documents": result.get("documents", [])
        }
    except Exception as e:
        logger.error(f"Engine Error: {str(e)}")
        error_msg = "A technical error occurred. Please ensure all API keys (Groq, Cohere) are correctly configured in the .env file."
        if "rate_limit_exceeded" in str(e).lower():
            error_msg = "The system is currently experiencing high traffic (Rate Limit Reached). Please try again in a few seconds."
        
        return {
            "answer": error_msg,
            "intent": "ERROR",
            "hallucination_check": False
        }
