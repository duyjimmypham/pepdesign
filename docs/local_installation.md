# Local Installation Guide (Without Docker)

This guide explains how to install and use PepDesign's computational tools **directly on your system** without Docker.

---

## Overview

You have two options:

1. **Use Stub Mode** - Fast prototyping without real tools (already works!)
2. **Install Tools Locally** - Real predictions on your machine

---

## Option 1: Stub Mode (Recommended for Development)

**Already working!** Your pipeline uses `MockRunner` automatically when Docker isn't available.

```python
from pepdesign.config import PipelineConfig, BackboneConfig, DesignConfig

config = PipelineConfig(
    # ... other settings ...
    backbone=BackboneConfig(
        generator_type="stub",  # ✅ Works now
        num_backbones=10
    ),
    design=DesignConfig(
        designer_type="stub",  # ✅ Works now
        num_sequences_per_backbone=5
    )
)
```

**What stub mode does**:

- Generates toy macrocycle backbones
- Creates random sequences
- Runs full pipeline logic
- Perfect for testing and development

---

## Option 2: Local Tool Installation

### Prerequisites

- Python 3.10+
- CUDA 11.8+ (for GPU tools)
- ~50GB disk space for model weights

---

### ProteinMPNN (Easiest)

```bash
# Clone repository
git clone https://github.com/dauparas/ProteinMPNN.git
cd ProteinMPNN

# Install dependencies
pip install torch numpy biopython

# Download model weights
mkdir -p ca_model_weights
cd ca_model_weights
wget https://github.com/dauparas/ProteinMPNN/raw/main/ca_model_weights/v_48_020.pt
```

**Configure PepDesign**:

```python
from pepdesign.runners import LocalRunner

# In pepdesign/external/protein_mpnn.py, modify:
class ProteinMPNNDesigner:
    def __init__(self, runner=None):
        # Use LocalRunner instead of DockerRunner
        self.runner = runner or LocalRunner(
            cwd="/path/to/ProteinMPNN"
        )
```

---

### RFdiffusion (Advanced)

```bash
# Clone repository
git clone https://github.com/RosettaCommons/RFdiffusion.git
cd RFdiffusion

# Install dependencies
pip install torch==2.0.1
pip install dgl==1.1.2+cu118 -f https://data.dgl.ai/wheels/cu118/repo.html
pip install -e .

# Download model weights
mkdir models
cd models
# Follow instructions at: https://github.com/RosettaCommons/RFdiffusion#models
```

**Configure PepDesign**:

```python
from pepdesign.runners import LocalRunner

# In pepdesign/external/rfdiffusion.py, modify:
class RFdiffusionGenerator:
    def __init__(self, runner=None):
        self.runner = runner or LocalRunner(
            cwd="/path/to/RFdiffusion"
        )
```

---

### ColabFold (AlphaFold2 - Recommended for Structure Prediction)

**Easiest via Conda**:

```bash
# Create conda environment
conda create -n colabfold python=3.10
conda activate colabfold

# Install ColabFold
pip install "colabfold[alphafold]@git+https://github.com/sokrypton/ColabFold"

# Install JAX with CUDA (if you have GPU)
pip install jax[cuda11_pip]==0.4.13 -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# Setup databases (optional - can skip for faster setup)
# colabfold_search will download on-the-fly
```

**Configure PepDesign**:

```python
from pepdesign.runners import LocalRunner

# In pepdesign/external/alphafold2.py, modify:
class AlphaFold2Predictor:
    def __init__(self, runner=None):
        self.runner = runner or LocalRunner()
        # colabfold_batch is now in PATH
```

---

## Recommended Workflow (Without Docker)

### Step 1: Start with Stub Mode

```python
config = PipelineConfig(
    backbone=BackboneConfig(generator_type="stub"),
    design=DesignConfig(designer_type="stub"),
    prediction=PredictionConfig(predictor_type="none")
)
```

### Step 2: Add ProteinMPNN (Easiest Real Tool)

```python
config = PipelineConfig(
    backbone=BackboneConfig(generator_type="stub"),  # Keep stub
    design=DesignConfig(designer_type="protein_mpnn"),  # Real tool!
    prediction=PredictionConfig(predictor_type="none")
)
```

### Step 3: Add Structure Prediction

```python
config = PipelineConfig(
    backbone=BackboneConfig(generator_type="stub"),
    design=DesignConfig(designer_type="protein_mpnn"),
    prediction=PredictionConfig(predictor_type="alphafold2")  # ColabFold
)
```

### Step 4: Full Pipeline (Advanced)

```python
config = PipelineConfig(
    backbone=BackboneConfig(generator_type="rfdiffusion"),  # All real tools
    design=DesignConfig(designer_type="protein_mpnn"),
    prediction=PredictionConfig(predictor_type="alphafold2")
)
```

---

## Cloud Alternatives (No Local GPU Needed)

### Google Colab

Run PepDesign in a Jupyter notebook with free GPU:

```python
# Install in Colab
!git clone https://github.com/duyjimmypham/pepdesign.git
!cd pepdesign && pip install -r requirements.txt

# Run pipeline
from pepdesign.pipeline import PepDesignPipeline
# ... your code ...
```

### AlphaFold Server (Free)

Use Google's free AlphaFold Server instead of local installation:

- https://alphafoldserver.com/
- Upload sequences manually
- Download predicted structures
- Import into PepDesign for analysis

---

## Troubleshooting

### Issue: CUDA not available

**Solution**: Use CPU mode (slower but works)

```python
import torch
torch.cuda.is_available()  # Check if GPU is detected

# If False, tools will run on CPU automatically
```

### Issue: Out of memory

**Solution**: Reduce batch sizes or use smaller models

```python
config = PipelineConfig(
    backbone=BackboneConfig(num_backbones=5),  # Reduce from 10
    design=DesignConfig(num_sequences_per_backbone=3)  # Reduce from 5
)
```

### Issue: Tool not found

**Solution**: Use absolute paths

```python
from pepdesign.runners import LocalRunner

runner = LocalRunner(
    cwd="C:/Users/YourName/ProteinMPNN"  # Absolute path
)
```

---

## Performance Comparison

| Setup                            | Speed  | GPU Required | Disk Space | Ease   |
| -------------------------------- | ------ | ------------ | ---------- | ------ |
| Stub Mode                        | ⚡⚡⚡ | ❌ No        | ~1GB       | ⭐⭐⭐ |
| Local ProteinMPNN                | ⚡⚡   | ❌ No        | ~5GB       | ⭐⭐   |
| Local ColabFold                  | ⚡     | ✅ Yes       | ~20GB      | ⭐     |
| Local RFdiffusion                | ⚡     | ✅ Yes       | ~30GB      | ⭐     |
| Google Colab                     | ⚡⚡   | ✅ Free      | 0GB        | ⭐⭐⭐ |
| Docker (requires virtualization) | ⚡⚡   | ✅ Yes       | ~40GB      | ⭐⭐   |

---

## Next Steps

**For your situation (no virtualization)**:

1. ✅ **Use stub mode** for development (already works!)
2. ✅ **Install ProteinMPNN locally** (easiest real tool, no GPU needed)
3. ✅ **Use Google Colab** for structure prediction (free GPU)

**Recommended starting point**:

```python
# This works RIGHT NOW without any installation:
from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import PipelineConfig, GlobalConfig, TargetConfig, BackboneConfig, DesignConfig, ScoringConfig

config = PipelineConfig(
    global_settings=GlobalConfig(output_dir="output/test"),
    target=TargetConfig(
        pdb_path="examples/target.pdb",
        mode="de_novo",
        target_chain="A",
        binding_site_residues=[1, 2, 3]
    ),
    backbone=BackboneConfig(generator_type="stub", num_backbones=5),
    design=DesignConfig(designer_type="stub", num_sequences_per_backbone=3),
    scoring=ScoringConfig()
)

pipeline = PepDesignPipeline(config)
pipeline.run()  # ✅ Works immediately!
```

Would you like me to help you:

1. Run the pipeline in stub mode right now?
2. Set up ProteinMPNN locally?
3. Create a Google Colab notebook?
