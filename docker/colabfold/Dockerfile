FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    python3.10 \
    python3-pip \
    hmmer \
    kalign \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install ColabFold
RUN pip3 install --no-cache-dir \
    "colabfold[alphafold]@git+https://github.com/sokrypton/ColabFold" \
    && pip3 install --no-cache-dir \
    jax[cuda11_pip]==0.4.13 -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# Setup ColabFold databases (optional - can be mounted)
RUN mkdir -p /databases

# Create directories
RUN mkdir -p /input /output

# Set environment variables
ENV COLABFOLD_DB=/databases

# Default command
CMD ["colabfold_batch", "--help"]
