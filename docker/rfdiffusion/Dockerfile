FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Prevent interactive prompts
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

# Clone RFdiffusion
RUN git clone https://github.com/RosettaCommons/RFdiffusion.git /app/RFdiffusion

# Install Python dependencies
WORKDIR /app/RFdiffusion
RUN pip3 install --no-cache-dir \
    torch==2.0.1 \
    numpy \
    hydra-core \
    pyrsistent \
    dgl==1.1.2+cu118 -f https://data.dgl.ai/wheels/cu118/repo.html \
    && pip3 install -e .

# Download model weights
# NOTE: Users must mount their own model weights directory
# Example: docker run -v /path/to/weights:/models rfdiffusion:latest
RUN mkdir -p /models

# Set environment variables
ENV PYTHONPATH=/app/RFdiffusion:$PYTHONPATH
ENV DGLBACKEND=pytorch

# Default command
CMD ["python3", "scripts/run_inference.py", "--help"]
