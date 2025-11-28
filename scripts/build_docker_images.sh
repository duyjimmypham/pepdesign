#!/bin/bash
# Build script for all PepDesign Docker images

set -e  # Exit on error

echo "Building PepDesign Docker Images..."
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Build RFdiffusion
echo -e "${BLUE}[1/5] Building RFdiffusion...${NC}"
docker build -t rfdiffusion:latest -f docker/rfdiffusion/Dockerfile .
echo -e "${GREEN}✓ RFdiffusion built${NC}\n"

# Build ProteinMPNN
echo -e "${BLUE}[2/5] Building ProteinMPNN...${NC}"
docker build -t proteinmpnn:latest -f docker/proteinmpnn/Dockerfile .
echo -e "${GREEN}✓ ProteinMPNN built${NC}\n"

# Build DiffPepBuilder
echo -e "${BLUE}[3/5] Building DiffPepBuilder...${NC}"
docker build -t diffpepbuilder:latest -f docker/diffpepbuilder/Dockerfile .
echo -e "${GREEN}✓ DiffPepBuilder built${NC}\n"

# Build ColabFold (AlphaFold2)
echo -e "${BLUE}[4/5] Building ColabFold...${NC}"
docker build -t colabfold:latest -f docker/colabfold/Dockerfile .
echo -e "${GREEN}✓ ColabFold built${NC}\n"

# Build AlphaFold3
echo -e "${BLUE}[5/5] Building AlphaFold3...${NC}"
docker build -t alphafold3:latest -f docker/alphafold3/Dockerfile .
echo -e "${GREEN}✓ AlphaFold3 built${NC}\n"

echo "===================================="
echo -e "${GREEN}All images built successfully!${NC}"
echo ""
echo "Available images:"
docker images | grep -E "rfdiffusion|proteinmpnn|diffpepbuilder|colabfold|alphafold3"
echo ""
echo "Next steps:"
echo "1. Download model parameters (see docs/model_setup.md)"
echo "2. Test an image: docker run --rm rfdiffusion:latest python3 scripts/run_inference.py --help"
echo "3. Run pipeline with real tools!"
