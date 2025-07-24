import json

from langchain_core.documents import Document
from typing_extensions import TypedDict

from services import llm
from schemas.rag_schema import RAGOutput
from services.agent.vector_store import VectorStoreManager
from services.agent.prompts import chat_prompt, summary_prompt


class SessionState(TypedDict):
    chat_history: list[dict]
    user_msg: str
    route: str
    docs: list[Document] | None
    result: str


VALID_ROUTES = {"CALLBACK", "NEEDS_DOCS", "NO_DOCS"}

def classify_node(state: SessionState) -> dict:
    prompt = (
        "Return exactly one of the tokens below on a single line.\n"
        "Tokens: CALLBACK, NEEDS_DOCS, NO_DOCS\n\n"
        "USER:\n{msg}"
    ).format(msg=state["user_msg"])

    raw = llm.invoke(prompt).content or ""
    tokens = raw.strip().split()
    decision = tokens[0].upper() if tokens else "NO_DOCS"

    return {"route": decision}

def summarise_node(state: SessionState) -> dict:
    lines = [
        f"{m['role'].capitalize()}: {m['content'].strip()}"
        for m in state["chat_history"] if m["role"] in ("user", "assistant")
    ]
    promp = summary_prompt.format(chat_history="\n".join(lines))
    summary = llm.invoke(promp).content
    return {"result": summary}

def retrieve_node(state: SessionState, vs: VectorStoreManager) -> dict:
    rephrased = llm.invoke(
        f"Rewrite the next question standalone: {state['user_msg']}"
    ).content
    state["docs"] = vs.search(rephrased)
    return {"docs": state["docs"]}

def draft_answer_node(state: SessionState) -> dict:
    doc_context = "\n\n".join(d.page_content for d in state.get("docs") or [])
    prompt = chat_prompt.format(
        context=doc_context,
        chat_history=state["chat_history"],
        input=state["user_msg"]
    )
    answer: RAGOutput = llm.with_structured_output(RAGOutput).invoke(prompt)
    return {"result": json.dumps(answer.model_dump())}
