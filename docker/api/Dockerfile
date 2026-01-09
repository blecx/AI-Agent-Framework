FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install git (required for GitPython)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for mounted volumes
RUN mkdir -p /projectDocs /config

# Expose port
EXPOSE 8000

# Set environment variables
ENV PROJECT_DOCS_PATH=/projectDocs
ENV LLM_CONFIG_PATH=/config/llm.json
ENV PYTHONUNBUFFERED=1

# Configure git (required for commits)
RUN git config --global user.email "agent@iso21500.local" && \
    git config --global user.name "ISO21500 Agent"

# Run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
