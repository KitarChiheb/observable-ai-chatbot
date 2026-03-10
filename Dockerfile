# Dockerfile for the observable AI chatbot application
# Uses Python 3.11 slim image for optimal size and performance

FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for the application
# curl is needed for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better Docker layer caching
# This ensures dependencies are only rebuilt when requirements.txt changes
COPY requirements.txt .

# Install Python dependencies from requirements.txt
# --no-cache-dir reduces image size by avoiding pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files to the container
# This is done after installing dependencies to optimize caching
COPY . .

# Create non-root user for security (best practice)
# Running as root is discouraged in production containers
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port 8000 for FastAPI application
EXPOSE 8000

# Health check to verify the application is running
# Uses the /health endpoint for proper application-level monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the FastAPI application with uvicorn server
# --host 0.0.0.0 makes it accessible from outside the container
# --port 8000 matches the exposed port
# --workers 1 is sufficient for this simple application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
