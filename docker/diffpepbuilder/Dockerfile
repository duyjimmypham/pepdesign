FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone DiffPepBuilder
RUN git clone https://github.com/YuzheWangPKU/DiffPepBuilder.git /app/DiffPepBuilder

# Install Python dependencies
WORKDIR /app/DiffPepBuilder
RUN pip3 install --no-cache-dir \
    torch \
    numpy \
    biopython \
    && pip3 install --no-cache-dir -r requirements.txt || true

# NOTE: Model weights should be included in the repo or downloaded separately
# Check the repository for specific instructions

# Set environment variables
ENV PYTHONPATH=/app/DiffPepBuilder:$PYTHONPATH

# Create directories
RUN mkdir -p /input /output

# Default command
CMD ["python3", "inference.py", "--help"]
