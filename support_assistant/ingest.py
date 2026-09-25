
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# Resolve paths relative to this script, regardless of
# the directory from which it is executed.
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DB_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    # 1. Load the eight policy documents.
    document_paths = sorted(DOCS_DIR.glob("doc_*.txt"))

    if len(document_paths) != 8:
        raise ValueError(
            f"Expected 8 policy documents, found {len(document_paths)}"
        )

    documents = [
        path.read_text(encoding="utf-8").strip()
        for path in document_paths
    ]

    if any(not document for document in documents):
        raise ValueError("One or more policy documents are empty.")

    print(f"Loaded {len(documents)} policy documents.")

    # 2. Use one chunk per document.
    # The assignment permits this because the policies are short.
    print("Loading the embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Generating embeddings...")
    embeddings = model.encode(
        documents,
        normalize_embeddings=True
    ).tolist()

    # 3. Create a persistent ChromaDB collection.
    client = chromadb.PersistentClient(path=str(DB_DIR))

    # Recreate the collection so rerunning ingestion
    # does not leave outdated or duplicate documents.
    existing_collections = [
        collection.name for collection in client.list_collections()
    ]

    if COLLECTION_NAME in existing_collections:
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    collection.add(
        ids=[path.stem for path in document_paths],
        documents=documents,
        embeddings=embeddings,
        metadatas=[
            {"source": path.name}
            for path in document_paths
        ]
    )

    print(f"Stored {collection.count()} chunks in ChromaDB.")

    # 4. Test retrieval using a sample customer question.
    question = "How long does it take to receive a refund?"

    question_embedding = model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=question_embedding,
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    print(f"\nTest question: {question}")
    print("\nTop 3 retrieved documents:")

    for rank, (metadata, distance) in enumerate(
        zip(
            results["metadatas"][0],
            results["distances"][0]
        ),
        start=1
    ):
        print(
            f"{rank}. {metadata['source']} "
            f"(cosine distance: {distance:.4f})"
        )


if __name__ == "__main__":
    main()
