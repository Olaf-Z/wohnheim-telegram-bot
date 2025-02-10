# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/
COPY data/ ./data/

# Set environment variables
ENV PYTHONPATH=/app
ENV DATA_FILE_DIRECTORY=/app/data

# Run the bot
CMD ["python3", "src/SteilerWohnheimsBot.py"]
