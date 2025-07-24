from langgraph.graph import StateGraph, END

from services.agent.vector_store import VectorStoreManager
from services.agent.nodes import SessionState, classify_node, summarise_node, retrieve_node, draft_answer_node


def build_graph(vs: VectorStoreManager):
    g = StateGraph(SessionState)
    g.add_node("classify", classify_node)
    g.add_node("summarise", lambda s: summarise_node(s))
    g.add_node("retrieve",  lambda s: retrieve_node(s, vs))
    g.add_node("answer",    lambda s: draft_answer_node(s))

    g.set_entry_point("classify")

    g.add_conditional_edges(
        "classify",
        lambda s: s["route"],
        {
            "CALLBACK": "summarise",
            "NEEDS_DOCS": "retrieve",
            "NO_DOCS": "answer",
        },
    )
    g.add_edge("summarise", END)
    g.add_edge("retrieve",  "answer")
    g.add_edge("answer",    END)
    return g.compile()
