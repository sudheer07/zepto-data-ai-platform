
import os
from pathlib import Path
from typing import Literal, TypedDict

import chromadb
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# The required, graded baseline uses mock mode.
MOCK_LLM = os.getenv("MOCK_LLM", "1") != "0"

POLICY_KEYWORDS = [
    "delivery",
    "return",
    "refund",
    "membership",
    "tracking",
    "cancel",
    "gift card",
    "support hours",
]


# --------------------------------------------------
# 1. Pydantic response schema
# --------------------------------------------------

class AssistantResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


# --------------------------------------------------
# 2. LangGraph state
# --------------------------------------------------

class AssistantState(TypedDict, total=False):
    query: str
    intent: Literal["policy_question", "general_question"]
    answer: str
    sources: list[str]
    confidence: float


# --------------------------------------------------
# 3. Load the embedding model and ChromaDB
# --------------------------------------------------

model = SentenceTransformer(MODEL_NAME)

client = chromadb.PersistentClient(path=str(DB_DIR))

collection = client.get_collection(
    name=COLLECTION_NAME
)


# --------------------------------------------------
# 4. Define the three graph nodes
# --------------------------------------------------

def classify_intent(state: AssistantState) -> dict:
    """Classify the customer question."""

    query = state["query"].lower()

    if MOCK_LLM:
        # Required mock-mode keyword heuristic.
        intent = (
            "policy_question"
            if any(keyword in query for keyword in POLICY_KEYWORDS)
            else "general_question"
        )
    else:
        raise NotImplementedError(
            "Real LLM mode is an optional extension. "
            "Run with MOCK_LLM=1."
        )

    return {"intent": intent}


def retrieve_and_answer(state: AssistantState) -> dict:
    """Retrieve the three closest policy chunks."""

    query_embedding = model.encode(
        [state["query"]],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    documents = results["documents"][0]
    document_ids = results["ids"][0]

    if not documents:
        return {
            "answer": "No relevant policy documents were found.",
            "sources": [],
            "confidence": 0.0,
        }

    if MOCK_LLM:
        # The graded baseline uses real retrieval but
        # does not make any LLM API calls.
        top_chunk_snippet = documents[0][:200]

        answer = (
            f"Based on the retrieved context: "
            f"{top_chunk_snippet}"
        )
    else:
        raise NotImplementedError(
            "Real LLM generation is an optional extension. "
            "Run with MOCK_LLM=1."
        )

    return {
        "answer": answer,
        "sources": document_ids,
        "confidence": 1.0,
    }


def direct_answer(state: AssistantState) -> dict:
    """Answer general questions without retrieval."""

    if MOCK_LLM:
        answer = (
            "I can only answer questions about "
            "Zepto policies right now."
        )
    else:
        raise NotImplementedError(
            "Real LLM generation is an optional extension. "
            "Run with MOCK_LLM=1."
        )

    return {
        "answer": answer,
        "sources": [],
        "confidence": 1.0,
    }


# --------------------------------------------------
# 5. Conditional routing
# --------------------------------------------------

def route_by_intent(
    state: AssistantState,
) -> Literal["retrieve_and_answer", "direct_answer"]:

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


# --------------------------------------------------
# 6. Build the LangGraph workflow
# --------------------------------------------------

workflow = StateGraph(AssistantState)

workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_and_answer", retrieve_and_answer)
workflow.add_node("direct_answer", direct_answer)

workflow.add_edge(START, "classify_intent")

workflow.add_conditional_edges(
    "classify_intent",
    route_by_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer",
    },
)

workflow.add_edge("retrieve_and_answer", END)
workflow.add_edge("direct_answer", END)

graph = workflow.compile()


# --------------------------------------------------
# 7. Run the assistant and validate its response
# --------------------------------------------------

def ask_assistant(query: str) -> AssistantResponse:
    result = graph.invoke({"query": query})

    return AssistantResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"],
    )


# --------------------------------------------------
# 8. Test both graph routes
# --------------------------------------------------

if __name__ == "__main__":
    questions = [
        "How long does it take to receive a refund?",
        "What is the capital of France?",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")

        response = ask_assistant(question)

        print(
            response.model_dump_json(indent=2)
        )
