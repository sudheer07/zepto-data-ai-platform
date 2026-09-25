
# Zepto Customer Support Assistant

A retrieval-augmented customer support assistant built using
Sentence Transformers, ChromaDB, LangGraph, Pydantic and FastAPI.
The application runs in mock LLM mode by default and can be
executed locally or in Docker.

The policy documents are illustrative examples created for this
capstone, not official Zepto policies.

## Architecture

1. Eight sample policy documents are loaded from `docs/`.
2. `ingest.py` generates embeddings using
   `sentence-transformers/all-MiniLM-L6-v2`.
3. Embeddings and document text are stored in a persistent
   ChromaDB collection using cosine similarity.
4. `assistant.py` implements a three-node LangGraph workflow:
   - `classify_intent`: Routes policy and general questions.
   - `retrieve_and_answer`: Retrieves the top three relevant
     documents and produces a mock answer.
   - `direct_answer`: Returns a canned response for general questions.
5. Pydantic validates the structured response.
6. `main.py` exposes the assistant through a FastAPI endpoint.

## Policy Documents

The eight sample documents cover delivery, returns and refunds,
membership, order tracking, cancellations, damaged or missing
items, gift cards, and customer support hours.

## Response Format

The `POST /ask` endpoint accepts a JSON object containing a
non-empty `query` string.

It returns:
- `answer`: The generated response.
- `sources`: IDs of retrieved policy documents.
- `confidence`: A number between 0 and 1.

## Run Locally

From the project root, activate a Python 3.11 virtual environment
and install the dependencies:

```bash
pip install -r support_assistant/requirements.txt
cd support_assistant
python ingest.py
uvicorn main:app --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000`.
Interactive API documentation is available at
`http://127.0.0.1:8000/docs`.

## Run with Docker

From the `support_assistant` directory:

```bash
docker build -t zepto-support-assistant .
docker run --rm -p 7860:7860 zepto-support-assistant
```

The Docker build installs CPU-only PyTorch and runs document
ingestion. The API is available at `http://127.0.0.1:7860`.

## API Examples

### Policy question

```bash
curl -s -X POST "http://127.0.0.1:7860/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"How long does it take to receive a refund?"}'
```

Actual response from the Docker container:

```json
{
  "answer": "Based on the retrieved context: Returns & Refunds\n\nGrocery and perishable items may be reported for a return within 24 hours of delivery if damaged, spoiled, or incorrect; non-perishable packaged items may be returned within 7 days ",
  "sources": ["doc_02", "doc_06", "doc_08"],
  "confidence": 1.0
}
```

### General question

```bash
curl -s -X POST "http://127.0.0.1:7860/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the capital of France?"}'
```

Actual response from the Docker container:

```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

## Prompt Design

`prompt_template.py` defines structured prompts containing a
role, context, task, output format and length constraints.
The policy prompt includes a negative constraint against using
information outside the retrieved context and a few-shot example.

The default `MOCK_LLM=1` mode uses deterministic responses rather
than calling an external LLM. Real LLM integration is not enabled
in this baseline implementation.

## Testing

The Docker image was successfully built on an Apple Silicon Mac.
Both the policy-question and general-question API requests were
tested successfully against the running container.