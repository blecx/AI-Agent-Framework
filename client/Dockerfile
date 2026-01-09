FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy client source code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app

# Default command (can be overridden in docker-compose or docker run)
CMD ["python", "-m", "src.client", "--help"]
