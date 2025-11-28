# Build script for all PepDesign Docker images (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "Building PepDesign Docker Images..." -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Build RFdiffusion
Write-Host "[1/5] Building RFdiffusion..." -ForegroundColor Blue
docker build -t rfdiffusion:latest -f docker/rfdiffusion/Dockerfile .
Write-Host "RFdiffusion built successfully" -ForegroundColor Green
Write-Host ""

# Build ProteinMPNN
Write-Host "[2/5] Building ProteinMPNN..." -ForegroundColor Blue
docker build -t proteinmpnn:latest -f docker/proteinmpnn/Dockerfile .
Write-Host "ProteinMPNN built successfully" -ForegroundColor Green
Write-Host ""

# Build DiffPepBuilder
Write-Host "[3/5] Building DiffPepBuilder..." -ForegroundColor Blue
docker build -t diffpepbuilder:latest -f docker/diffpepbuilder/Dockerfile .
Write-Host "DiffPepBuilder built successfully" -ForegroundColor Green
Write-Host ""

# Build ColabFold (AlphaFold2)
Write-Host "[4/5] Building ColabFold..." -ForegroundColor Blue
docker build -t colabfold:latest -f docker/colabfold/Dockerfile .
Write-Host "ColabFold built successfully" -ForegroundColor Green
Write-Host ""

# Build AlphaFold3
Write-Host "[5/5] Building AlphaFold3..." -ForegroundColor Blue
docker build -t alphafold3:latest -f docker/alphafold3/Dockerfile .
Write-Host "AlphaFold3 built successfully" -ForegroundColor Green
Write-Host ""

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "All images built successfully" -ForegroundColor Green
Write-Host ""
Write-Host "Available images:"
docker images | Select-String -Pattern "rfdiffusion|proteinmpnn|diffpepbuilder|colabfold|alphafold3"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Download model parameters (see docs/model_setup.md)"
Write-Host "2. Test an image: docker run --rm rfdiffusion:latest python3 scripts/run_inference.py --help"
Write-Host "3. Run pipeline with real tools"
