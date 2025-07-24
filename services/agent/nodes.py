import json

from langchain_core.documents import Document
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage

from services import llm, langfuse_handler
from schemas.rag_schema import RAGOutput, Language
from services.agent.vector_store import VectorStoreManager
from services.agent.prompts import chat_prompt, summary_prompt, chat_no_context_prompt, classifier_prompt


class SessionState(TypedDict):
    chat_history: list[dict]
    user_msg: str
    route: str
    docs: list[Document] | None
    result: str
    language: Language


VALID_ROUTES = {"CALLBACK", "NEEDS_DOCS", "NO_DOCS"}

def classify_node(state: SessionState) -> dict:
    prompt = classifier_prompt.format(user_msg=state["user_msg"])
    raw = llm.invoke(
        prompt,
        config={"callbacks": [langfuse_handler]},
    ).content or ""
    tokens = raw.strip().split()
    decision = tokens[0].upper() if tokens else "NO_DOCS"
    
    print("--------------------------------")
    print("decision: ", decision)
    print("--------------------------------")

    return {"route": decision}

def summarise_node(state: SessionState) -> dict:
    msgs = []
    for m in state["chat_history"]:
        if m["role"] == "user":
            msgs.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            msgs.append(AIMessage(content=m["content"]))

    prompt_val = summary_prompt.format(
        chat_history=msgs,
        input="Please summarize the conversation in a short and concise manner.",
        language=state["language"]
    )

    summary = llm.invoke(
            prompt_val,
            config={"callbacks": [langfuse_handler]},
        ).content
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
    doc_context = "\n\n".join(d.page_content for d in state.get("docs") or [])
    prompt = chat_prompt if doc_context else chat_no_context_prompt
    prompt = prompt.format(
        context=doc_context,
        chat_history=state["chat_history"],
        input=state["user_msg"],
        language=state["language"]
    )
    answer: RAGOutput = llm.with_structured_output(RAGOutput).invoke(
        prompt,
        config={"callbacks": [langfuse_handler]},
    )
    print("--------------------------------")
    print("answer: ", answer)
    print("--------------------------------")
    return {"result": json.dumps(answer.model_dump())}
