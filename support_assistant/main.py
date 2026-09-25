
from fastapi import FastAPI
from pydantic import BaseModel, Field

from assistant import AssistantResponse, ask_assistant


app = FastAPI(
    title="Zepto Support Assistant",
    description="A LangGraph and ChromaDB-based support assistant.",
    version="1.0.0",
)


class AskRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="The customer's question",
    )


@app.get("/")
def home():
    return {
        "message": "Zepto Support Assistant API is running"
    }


@app.post("/ask", response_model=AssistantResponse)
def ask(request: AskRequest):
    return ask_assistant(request.query)
