# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environmental variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    bluez \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY test-scripts/requirements.txt /app/

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pytest pytest-asyncio

# Copy the rest of the application files
COPY test-scripts/ /app/test-scripts/

# Copy guidelines or metadata if needed
COPY agent-guidelines.md /app/

# Set working directory to test-scripts
WORKDIR /app/test-scripts

# Default command runs the test suite
CMD ["pytest", "-v"]
