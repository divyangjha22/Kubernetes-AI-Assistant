from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node
from app.agents.nodes.retriever import retrieve_node
from app.agents.nodes.responder import generate_node

# 1. Initialize the State Graph
workflow = StateGraph(AgentState)

# 2. Define the Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retrieve_node)
workflow.add_node("responder", generate_node)

# 3. Define the Edges & Routing Logic
def route_planner(state: AgentState):
    """Routes the workflow based on the planner's decision."""
    if state["current_query"] == "CONVERSATIONAL":
        return "responder"
    return "retriever"

# --- Routing logic for retriever results ---
def route_retriever(state: AgentState):
    """Routes to responder if documents exist, otherwise ends early."""
    docs = state.get("documents", [])
    if not docs:
        return END
    return "responder"

workflow.set_entry_point("planner")

# Conditional Edge: Planner -> Router -> (Retriever OR Responder)
workflow.add_conditional_edges(
    "planner",
    route_planner,
    {
        "retriever": "retriever",
        "responder": "responder"
    }
)

workflow.add_conditional_edges(
    "retriever",
    route_retriever,
    {
        "responder": "responder",
        END: END
    }
)

workflow.add_edge("responder", END)

# MEMORY UPGRADE - MemorySaver allows the agent to remember conversations based on 'thread_id'
checkpointer = MemorySaver()

# 4. Compile the Graph with Memory
rag_agent = workflow.compile(checkpointer=checkpointer)
