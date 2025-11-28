FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    python3.10 \
    python3-pip \
    hmmer \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone AlphaFold3 repository
RUN git clone https://github.com/google-deepmind/alphafold3.git /app/alphafold3

# Install Python dependencies
WORKDIR /app/alphafold3
RUN pip3 install --no-cache-dir -r requirements.txt

# CRITICAL: Model parameters must be obtained separately
# See: https://github.com/google-deepmind/alphafold3#obtaining-model-parameters
# Users must mount model directory: -v /path/to/af3_models:/models

# Create directories
RUN mkdir -p /input /output /models /databases

# Set environment variables
ENV PYTHONPATH=/app/alphafold3:$PYTHONPATH
ENV AF3_MODEL_DIR=/models

# Default command
CMD ["python3", "run_alphafold.py", "--help"]
