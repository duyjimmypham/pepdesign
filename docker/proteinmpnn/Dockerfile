FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone ProteinMPNN
RUN git clone https://github.com/dauparas/ProteinMPNN.git /app/ProteinMPNN

# Install Python dependencies
WORKDIR /app/ProteinMPNN
RUN pip install --no-cache-dir \
    torch \
    numpy \
    && pip install --no-cache-dir \
    biopython

# Download model weights
RUN mkdir -p /app/ProteinMPNN/ca_model_weights && \
    cd /app/ProteinMPNN/ca_model_weights && \
    wget -q https://github.com/dauparas/ProteinMPNN/raw/main/ca_model_weights/v_48_020.pt

# Set environment variables
ENV PYTHONPATH=/app/ProteinMPNN:$PYTHONPATH

# Create directories for input/output
RUN mkdir -p /input /output

# Default command
CMD ["python", "protein_mpnn_run.py", "--help"]
