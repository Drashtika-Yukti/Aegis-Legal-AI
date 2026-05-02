from core.router import router
from core.memory import memory
from core.graph import nexus_graph
from langchain_core.messages import HumanMessage
from core.logger import get_logger

logger = get_logger("AegisEngine")

async def run_aegis_stream(query: str, session_id: str = "default"):
    """
    Aegis Master Entry Point (Streaming).
    Yields JSON events for the frontend.
    """
    logger.info(f"Session {session_id} | Starting stream.")

    try:
        # 1. Routing Status
        yield {"type": "status", "content": "Analyzing legal intent..."}
        intent_result = router.route(query)
        
        if intent_result.category == "GREETING":
            yield {"type": "token", "content": "Hello! I am Aegis, your Legal Intelligence Assistant. How can I help you today?"}
            return

        # 2. Graph Streaming
        # We use astream_events to catch tokens from the 'generate' node
        async for event in nexus_graph.astream_events(
            {"original_query": query, "messages": []},
            version="v2"
        ):
            kind = event["event"]
            node = event.get("metadata", {}).get("langgraph_node", "")

            # Stream Status Updates
            if kind == "on_chain_start" and node:
                status_map = {
                    "mask": "Shielding sensitive identifiers...",
                    "retrieve": "Searching law library...",
                    "grade": "Verifying document relevance...",
                    "generate": "Drafting legal insight...",
                    "judge": "Performing hallucination check..."
                }
                if node in status_map:
                    yield {"type": "status", "content": status_map[node]}

            # Stream Chat Tokens (from the generate node)
            if kind == "on_chat_model_stream" and node == "generate":
                content = event["data"]["chunk"].content
                if content:
                    yield {"type": "token", "content": content}

            # Final Data (from the end of the chain)
            if kind == "on_chain_end" and node == "unmask":
                result = event["data"]["output"]
                yield {
                    "type": "final",
                    "documents": result.get("documents", []),
                    "hallucination_check": not result.get("hallucination_detected", False)
                }

    except Exception as e:
        logger.error(f"Stream Error: {str(e)}", exc_info=True)
        yield {
            "type": "error",
            "content": "Aegis has encountered a legal paradox. Our scribes are resolving the conflict."
        }
