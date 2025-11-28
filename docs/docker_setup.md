# Docker Setup Guide

This guide explains how to build and use Docker containers for PepDesign's computational tools.

---

## Prerequisites

### 1. Install Docker

**Windows**:

- Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
- Enable WSL 2 backend
- Restart your computer

**Linux**:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER  # Add your user to docker group
```

**macOS**:

- Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)

### 2. Install NVIDIA Docker (For GPU Support)

**Linux only** (Windows/Mac use Docker Desktop's built-in GPU support):

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 3. Verify Installation

```bash
# Test Docker
docker run hello-world

# Test GPU access (if applicable)
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

---

## Building Docker Images

### Option 1: Build All Images (Recommended)

**Linux/Mac**:

```bash
chmod +x scripts/build_docker_images.sh
./scripts/build_docker_images.sh
```

**Windows PowerShell**:

```powershell
.\scripts\build_docker_images.ps1
```

### Option 2: Build Individual Images

```bash
# RFdiffusion
docker build -t rfdiffusion:latest -f docker/rfdiffusion/Dockerfile .

# ProteinMPNN
docker build -t proteinmpnn:latest -f docker/proteinmpnn/Dockerfile .

# DiffPepBuilder
docker build -t diffpepbuilder:latest -f docker/diffpepbuilder/Dockerfile .

# ColabFold (AlphaFold2)
docker build -t colabfold:latest -f docker/colabfold/Dockerfile .

# AlphaFold3
docker build -t alphafold3:latest -f docker/alphafold3/Dockerfile .
```

### Option 3: Use Docker Compose

```bash
docker-compose build
```

---

## Running Docker Containers

### RFdiffusion

```bash
docker run --rm --gpus all \
  -v $(pwd)/models/rfdiffusion:/models \
  -v $(pwd)/data:/data \
  rfdiffusion:latest \
  python3 scripts/run_inference.py \
    --input_pdb=/data/target.pdb \
    --output_prefix=/data/output \
    --model_dir=/models
```

### ProteinMPNN

```bash
docker run --rm \
  -v $(pwd)/data:/data \
  proteinmpnn:latest \
  python protein_mpnn_run.py \
    --pdb_path=/data/backbone.pdb \
    --out_folder=/data/sequences
```

### ColabFold (AlphaFold2)

```bash
docker run --rm --gpus all \
  -v $(pwd)/models/alphafold2:/databases \
  -v $(pwd)/data:/data \
  colabfold:latest \
  colabfold_batch \
    /data/sequences.fasta \
    /data/predictions
```

### AlphaFold3

```bash
docker run --rm --gpus all \
  -v $(pwd)/models/alphafold3:/models \
  -v $(pwd)/data:/data \
  alphafold3:latest \
  python3 run_alphafold.py \
    --json_path=/data/input.json \
    --model_dir=/models \
    --output_dir=/data/predictions
```

---

## Using with PepDesign Pipeline

Once Docker images are built, PepDesign will automatically use them:

```python
from pepdesign.config import PipelineConfig, BackboneConfig

config = PipelineConfig(
    # ... other settings ...
    backbone=BackboneConfig(
        generator_type="rfdiffusion",  # Will use Docker automatically
        num_backbones=10
    )
)
```

**How it works**:

1. `DockerRunner` checks if the image exists
2. If yes → runs Docker container
3. If no → falls back to `MockRunner`

---

## Volume Mounting

### Directory Structure

```
PepDesign/
├── models/              # Model weights (excluded from git)
│   ├── rfdiffusion/
│   ├── proteinmpnn/
│   ├── alphafold2/
│   └── alphafold3/
├── data/                # Input/output data
└── docker/              # Dockerfiles
```

### Mount Points

| Container Path | Host Path             | Purpose             |
| -------------- | --------------------- | ------------------- |
| `/models`      | `./models/<tool>`     | Model parameters    |
| `/data`        | `./data`              | Input/output files  |
| `/databases`   | `./models/alphafold2` | AlphaFold databases |

---

## Troubleshooting

### Issue: "docker: command not found"

**Solution**: Install Docker (see Prerequisites)

### Issue: "permission denied while trying to connect to the Docker daemon"

**Solution**:

```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

### Issue: "could not select device driver with capabilities: [[gpu]]"

**Solution**: Install NVIDIA Docker runtime (see Prerequisites)

### Issue: Image build fails with "no space left on device"

**Solution**: Clean up Docker:

```bash
docker system prune -a
```

### Issue: Container can't access GPU

**Solution**:

1. Verify GPU: `nvidia-smi`
2. Test Docker GPU: `docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`
3. Check Docker Desktop settings (Windows/Mac)

### Issue: "Cannot connect to the Docker daemon"

**Solution**: Start Docker Desktop or Docker service:

```bash
# Linux
sudo systemctl start docker

# Windows/Mac: Start Docker Desktop application
```

---

## Performance Tips

### 1. Use BuildKit for Faster Builds

```bash
export DOCKER_BUILDKIT=1
docker build ...
```

### 2. Cache Layers

Docker caches each layer. Order Dockerfile commands from least to most frequently changing:

```dockerfile
# ✅ Good: Dependencies first (rarely change)
RUN pip install torch numpy
COPY . /app  # Code last (changes often)

# ❌ Bad: Code first
COPY . /app
RUN pip install torch numpy  # Reinstalls every time code changes
```

### 3. Multi-Stage Builds (Advanced)

Reduce final image size by using build stages.

---

## Security Best Practices

### 1. Don't Run as Root

Add to Dockerfile:

```dockerfile
RUN useradd -m -u 1000 user
USER user
```

### 2. Scan Images for Vulnerabilities

```bash
docker scan rfdiffusion:latest
```

### 3. Use Specific Base Image Tags

```dockerfile
# ✅ Good
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# ❌ Bad (version can change)
FROM nvidia/cuda:latest
```

---

## Next Steps

1. ✅ Build all Docker images
2. ✅ Download model parameters (see [model_setup.md](model_setup.md))
3. ✅ Test individual containers
4. ✅ Run PepDesign pipeline with real tools!

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [NVIDIA Docker](https://github.com/NVIDIA/nvidia-docker)
- [Docker Compose](https://docs.docker.com/compose/)
- [RFdiffusion Repo](https://github.com/RosettaCommons/RFdiffusion)
- [ProteinMPNN Repo](https://github.com/dauparas/ProteinMPNN)
- [AlphaFold3 Repo](https://github.com/google-deepmind/alphafold3)
