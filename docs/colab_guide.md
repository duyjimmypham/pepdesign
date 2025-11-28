# PepDesign on Google Colab

This notebook demonstrates how to run the PepDesign pipeline on Google Colab with ProteinMPNN and AlphaFold3.

## Setup

### 1. Install PepDesign

```python
# Clone repository
!git clone https://github.com/duyjimmypham/pepdesign.git
%cd pepdesign

# Install dependencies
!pip install -q -r requirements.txt
```

### 2. Install ProteinMPNN

```python
# Clone ProteinMPNN
!git clone https://github.com/dauparas/ProteinMPNN.git /content/ProteinMPNN
%cd /content/ProteinMPNN

# Download model weights
!mkdir -p ca_model_weights
!wget -q https://github.com/dauparas/ProteinMPNN/raw/main/ca_model_weights/v_48_020.pt -O ca_model_weights/v_48_020.pt

print("✅ ProteinMPNN installed")
```

### 3. Install AlphaFold3

```python
# Clone AlphaFold3
!git clone https://github.com/google-deepmind/alphafold3.git /content/alphafold3
%cd /content/alphafold3

# Install dependencies
!pip install -q -r requirements.txt

print("✅ AlphaFold3 installed")
print("⚠️ You must download model parameters separately (see below)")
```

### 4. Download AlphaFold3 Model Parameters

**IMPORTANT**: AlphaFold3 model parameters require registration.

1. Request access: https://forms.gle/svvpY4u2jsHEwWYS6
2. Once approved, download the parameters
3. Upload to Colab or mount from Google Drive:

```python
# Option A: Upload directly (slow)
from google.colab import files
uploaded = files.upload()  # Upload af3_params.tar.gz

# Option B: Mount Google Drive (recommended)
from google.colab import drive
drive.mount('/content/drive')

# Extract parameters
!mkdir -p /content/models/alphafold3
!tar -xzf /content/drive/MyDrive/af3_params.tar.gz -C /content/models/alphafold3

print("✅ AlphaFold3 parameters ready")
```

---

## Run PepDesign Pipeline

### Example: De Novo Peptide Design

```python
import sys
sys.path.append('/content/pepdesign')

from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import (
    PipelineConfig, GlobalConfig, TargetConfig,
    BackboneConfig, DesignConfig, ScoringConfig, PredictionConfig
)

# Upload your target PDB
from google.colab import files
print("Upload your target PDB file:")
uploaded = files.upload()
target_pdb = list(uploaded.keys())[0]

# Configure pipeline
config = PipelineConfig(
    global_settings=GlobalConfig(
        output_dir="/content/output",
        seed=42
    ),
    target=TargetConfig(
        pdb_path=target_pdb,
        mode="de_novo",
        target_chain="A",
        binding_site_residues=[25, 26, 29, 30, 32]  # Adjust for your target
    ),
    backbone=BackboneConfig(
        generator_type="stub",  # Use stub for backbone (or install RFdiffusion)
        num_backbones=5,
        peptide_length=12
    ),
    design=DesignConfig(
        designer_type="protein_mpnn",  # ✅ Real ProteinMPNN
        num_sequences_per_backbone=5
    ),
    scoring=ScoringConfig(
        charge_min=-2.0,
        charge_max=2.0,
        max_hydrophobic_fraction=0.6
    ),
    prediction=PredictionConfig(
        predictor_type="alphafold3",  # ✅ Real AlphaFold3
        top_n=3,
        num_models=1,
        model_dir="/content/models/alphafold3"
    )
)

# Run pipeline
pipeline = PepDesignPipeline(config)
pipeline.run()

print("✅ Pipeline complete!")
print("📁 Results in /content/output/")
```

---

## Download Results

```python
# Zip results
!zip -r results.zip /content/output/

# Download
from google.colab import files
files.download('results.zip')
```

---

## View Results in Colab

### View HTML Report

```python
from IPython.display import IFrame
IFrame('/content/output/report.html', width=1000, height=600)
```

### View Top Sequences

```python
import pandas as pd

# Load ranked sequences
df = pd.read_csv('/content/output/ranking/ranked.csv')
print("Top 5 Designs:")
print(df.head())
```

### Visualize Structures (if predicted)

```python
# Install py3Dmol
!pip install -q py3Dmol

import py3Dmol

# Load predicted structure
pdb_file = '/content/output/predictions/design_0_model_0.pdb'

with open(pdb_file, 'r') as f:
    pdb_data = f.read()

# Visualize
view = py3Dmol.view(width=800, height=600)
view.addModel(pdb_data, 'pdb')
view.setStyle({'cartoon': {'color': 'spectrum'}})
view.zoomTo()
view.show()
```

---

## Tips for Colab

### 1. Enable GPU

Runtime → Change runtime type → GPU (T4)

### 2. Check GPU Availability

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

### 3. Monitor Resources

```python
# Check RAM usage
!free -h

# Check GPU usage
!nvidia-smi
```

### 4. Save to Google Drive

```python
# Mount Drive
from google.colab import drive
drive.mount('/content/drive')

# Copy results
!cp -r /content/output /content/drive/MyDrive/pepdesign_results
```

---

## Troubleshooting

### Issue: "ProteinMPNN not found"

**Solution**: Make sure you're in the correct directory

```python
%cd /content/ProteinMPNN
!pwd
```

### Issue: "AlphaFold3 parameters not found"

**Solution**: Verify model directory

```python
!ls -lh /content/models/alphafold3
```

### Issue: "Out of memory"

**Solution**: Reduce batch sizes

```python
config = PipelineConfig(
    backbone=BackboneConfig(num_backbones=3),  # Reduce
    design=DesignConfig(num_sequences_per_backbone=3)  # Reduce
)
```

### Issue: "Session timeout"

**Solution**: Colab sessions last ~12 hours. For long runs:

1. Save intermediate results to Drive
2. Use checkpointing
3. Consider Colab Pro for longer sessions

---

## Next Steps

1. ✅ Run the example above
2. ✅ Adjust parameters for your target
3. ✅ Download and analyze results
4. ✅ Iterate on designs

**Happy designing! 🧬**
