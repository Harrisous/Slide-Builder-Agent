from langgraph.graph import StateGraph, END
from agents import AgentState, planner_node, retriever_node, assembler_node, reviewer_node

def should_continue(state: AgentState):
    feedback = state.get('feedback', "")
    revision_count = state.get('revision_count', 0)
    
    if feedback == "APPROVED":
        return END
    
    if revision_count >= 1: # 1 revision allowed for testing
        print("--- MAX REVISIONS REACHED ---")
        return END
        
    return "planner"

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("assembler", assembler_node)
    workflow.add_node("reviewer", reviewer_node)
    
    workflow.set_entry_point("planner")
    
    workflow.add_edge("planner", "retriever")
    workflow.add_edge("retriever", "assembler")
    workflow.add_edge("assembler", "reviewer")
    
    workflow.add_conditional_edges(
        "reviewer",
        should_continue,
        {
            END: END,
            "planner": "planner"
        }
    )
    
    return workflow.compile()
