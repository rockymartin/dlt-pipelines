# Multi-pipeline Dockerfile for dlt Pipelines (Pokemon & Chess)
# This Dockerfile can build images for both Pokemon and Chess pipelines

# Use Python 3.11 slim image for Cloud Run
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Set environment variables for Cloud Run
ENV PYTHONUNBUFFERED=1
ENV DLT_TELEMETRY=False

# Expose port (Cloud Run will override this)
EXPOSE 8080

# Default command - will be determined by build arg
ARG PIPELINE_TYPE=pokemon
ENV PIPELINE_TYPE=${PIPELINE_TYPE}

# Set the appropriate entry point based on pipeline type
CMD if [ "$PIPELINE_TYPE" = "chess" ]; then python chess_pipeline.py; else python pokemon_pipeline.py; fi
