
FROM python:3.11-slim

WORKDIR /app

# Install CPU-only PyTorch to avoid large NVIDIA CUDA downloads.
RUN pip install --no-cache-dir --timeout 120 --retries 5 \
    torch==2.5.1 \
    --index-url https://download.pytorch.org/whl/cpu

# Install the remaining Python dependencies.
COPY requirements.txt .

RUN pip install --no-cache-dir --timeout 120 --retries 5 \
    -r requirements.txt

# Configure the embedding model and mock mode.
ENV HF_HOME=/app/.cache/huggingface
ENV MOCK_LLM=1

# Copy the application and policy documents.
COPY . .

# Create the ChromaDB collection inside the image.
RUN python ingest.py

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]