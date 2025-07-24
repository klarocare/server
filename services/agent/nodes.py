import json

from langchain_core.documents import Document
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage

from services import llm
from schemas.rag_schema import RAGOutput
from services.agent.vector_store import VectorStoreManager
from services.agent.prompts import chat_prompt, summary_prompt, chat_no_context_prompt, classifier_prompt


class SessionState(TypedDict):
    chat_history: list[dict]
    user_msg: str
    route: str
    docs: list[Document] | None
    result: str


VALID_ROUTES = {"CALLBACK", "NEEDS_DOCS", "NO_DOCS"}

def classify_node(state: SessionState) -> dict:
    prompt = classifier_prompt.format(user_msg=state["user_msg"])
    raw = llm.invoke(prompt).content or ""
    tokens = raw.strip().split()
    decision = tokens[0].upper() if tokens else "NO_DOCS"
    
    print("--------------------------------")
    print("decision: ", decision)
    print("--------------------------------")

    return {"route": decision}

def summarise_node(state: SessionState) -> dict:
    # ── 1️⃣  Convert raw dicts → LangChain messages
    msgs = []
    for m in state["chat_history"]:
        if m["role"] == "user":
            msgs.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            msgs.append(AIMessage(content=m["content"]))

    # ── 2️⃣  Fill the ChatPromptTemplate
    prompt_val = summary_prompt.format(
        chat_history=msgs,
        input="Bitte fasse die Unterhaltung kurz in der Ich-Perspektive zusammen."
        # or simply "" if your system prompt already contains the instruction
    )

    # ── 3️⃣  Call the LLM & return
    summary = llm.invoke(prompt_val).content
    return {
        "result": summary
    }

def retrieve_node(state: SessionState, vs: VectorStoreManager) -> dict:
    rephrased = llm.invoke(
        f"Rewrite the next question standalone: {state['user_msg']}"
    ).content
    state["docs"] = vs.search(rephrased)
    print("--------------------------------")
    print("docs: ", state["docs"])
    print("--------------------------------")
    return {"docs": state["docs"]}

def draft_answer_node(state: SessionState) -> dict:
    print("--------------------------------")
    print("are there any docs?: ", state.get("docs"))
    print("--------------------------------")
    doc_context = "\n\n".join(d.page_content for d in state.get("docs") or [])
    prompt = chat_prompt if doc_context else chat_no_context_prompt
    prompt = prompt.format(
        context=doc_context,
        chat_history=state["chat_history"],
        input=state["user_msg"]
    )
    print("--------------------------------")
    print("prompt: ", prompt)
    print("--------------------------------")
    answer: RAGOutput = llm.with_structured_output(RAGOutput).invoke(prompt)
    print("--------------------------------")
    print("answer: ", answer)
    print("--------------------------------")
    return {"result": json.dumps(answer.model_dump())}
