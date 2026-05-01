from langgraph.graph import StateGraph, START, END
from core.state import AgentState
from agents.rag_nodes import nodes

def build_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("mask", nodes.mask_query)
    workflow.add_node("retrieve", nodes.retrieve)
    workflow.add_node("grade", nodes.grade_documents)
    workflow.add_node("generate", nodes.generate)
    workflow.add_node("judge", nodes.judge_answer)
    workflow.add_node("unmask", nodes.unmask_response)
    workflow.add_node("learn", nodes.extract_facts)

    # Build Edges
    workflow.add_edge(START, "mask")
    workflow.add_edge("mask", "retrieve")
    workflow.add_edge("retrieve", "grade")

    # Conditional Logic: If relevant, generate. If not, end with error.
    def decide_to_generate(state: AgentState):
        if state["is_relevant"]:
            return "generate"
        return END

    workflow.add_conditional_edges(
        "grade",
        decide_to_generate,
        {
            "generate": "generate",
            END: END
        }
    )

    workflow.add_edge("generate", "judge")
    workflow.add_edge("judge", "unmask")
    
    # Learn in parallel or after unmasking
    workflow.add_edge("unmask", "learn")
    workflow.add_edge("learn", END)

    return workflow.compile()

nexus_graph = build_graph()
