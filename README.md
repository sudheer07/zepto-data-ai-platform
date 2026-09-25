# Zepto Data & AI Platform

Capstone project for the Certificate Program
in Artificial Intelligence and Machine Learning.


# Zepto Data & AI Platform Capstone

An end-to-end Data & AI capstone project comprising a data
engineering pipeline, exploratory data analysis and machine
learning, and a retrieval-augmented customer support assistant.

## Project Structure

```text
zepto-data-ai-platform/
├── data_pipeline/
│   ├── scrape_books.py
│   ├── clean_books.py
│   ├── create_database.py
│   ├── run_queries.py
│   └── README.md
├── analytics/
│   ├── models/
│   └── README.md
├── support_assistant/
│   ├── docs/
│   ├── ingest.py
│   ├── assistant.py
│   ├── prompt_template.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .dockerignore
│   └── README.md
└── README.md
```

## Module 1: Data Engineering Pipeline

This module collects, cleans, stores and analyzes book data
from Books to Scrape.

- Scrapes 69 books across Mystery, Historical Fiction and Travel.
- Cleans the collected data and converts prices from GBP to INR.
- Stores the cleaned data in a normalized SQLite database.
- Executes six SQL queries and exports their results.
- Uses pandas for additional data analysis.

See [Module 1 README](data_pipeline/README.md) for setup,
execution instructions and outputs.

## Module 2: Data Analytics and Machine Learning

This module uses the Titanic dataset to demonstrate exploratory
data analysis and supervised machine learning.

- Explores the dataset and visualizes important patterns.
- Prepares features for machine learning.
- Trains and evaluates a classification model for survival.
- Trains and evaluates a regression model for passenger fare.
- Saves the selected classification model for reuse.

See [Module 2 README](analytics/README.md) for the analysis,
modeling approach and results.

## Module 3: AI Customer Support Assistant

This module implements a retrieval-augmented assistant using
eight illustrative customer support policy documents.

- Generates document embeddings using all-MiniLM-L6-v2.
- Stores and retrieves documents using ChromaDB.
- Uses a three-node LangGraph workflow for intent
  classification, retrieval and direct responses.
- Validates structured responses using Pydantic.
- Exposes a POST /ask endpoint using FastAPI.
- Runs in mock LLM mode by default.
- Includes a Dockerfile for containerized execution.

The Docker image was built successfully, and both policy and
general question API requests were tested against the
running container.

See [Module 3 README](support_assistant/README.md) for the
architecture, setup instructions and actual API responses.

## Technologies

Python 3.11, Beautiful Soup, pandas, SQLite, scikit-learn,
Sentence Transformers, ChromaDB, LangGraph, Pydantic,
FastAPI and Docker.

## Running the Project

Each module is self-contained and has its own README with
the relevant dependencies, commands and example outputs.

Start with:
- [Data Engineering Pipeline](data_pipeline/README.md)
- [Data Analytics](analytics/README.md)
- [AI Support Assistant](support_assistant/README.md)

## Git Workflow

Development was carried out using feature branches, with
module-specific commits merged into the main branch.

## Notes

The support assistant's policy documents are illustrative
examples for this capstone and should not be interpreted as
official Zepto policies.