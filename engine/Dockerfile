# --- STAGE 1: Build Stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build-essential for any C-based python extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- STAGE 2: Final Stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy ONLY necessary dependencies from builder
COPY --from=builder /install /usr/local

# SURGICAL COPY: Only copy what the engine needs
COPY core/ ./core/
COPY agents/ ./agents/
COPY utils/ ./utils/
COPY main.py .
COPY requirements.txt .

# Download spaCy model (Crucial for Privacy Shield)
RUN python -m spacy download en_core_web_sm

# Expose FastAPI port
EXPOSE 8000

# Run the production server using the corrected uvicorn module syntax
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
