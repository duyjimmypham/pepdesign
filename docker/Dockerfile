# Dockerfile for PepDesign
# Includes dependencies for ProteinMPNN and RFdiffusion

FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ProteinMPNN
RUN git clone https://github.com/dauparas/ProteinMPNN.git /app/ProteinMPNN

# Install RFdiffusion (Stub - requires manual setup for weights usually)
# RUN git clone https://github.com/RosettaCommons/RFdiffusion.git /app/RFdiffusion
# RUN pip install -e /app/RFdiffusion/env/SE3Transformer

# Copy PepDesign code
COPY . /app

# Set entrypoint
ENTRYPOINT ["python", "examples/mdm2_p53/run_pipeline_v2.py"]
