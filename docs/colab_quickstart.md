# Quick Start: PepDesign on Google Colab

**Goal**: Run real ProteinMPNN sequence design in 5 minutes.

---

## Step 1: Open Google Colab

1. Go to: https://colab.research.google.com/
2. Click **"New Notebook"** or **File → New Notebook**
3. **IMPORTANT**: Enable GPU
   - Click **Runtime → Change runtime type**
   - Set **Hardware accelerator** to **GPU (T4)**
   - Click **Save**

---

## Step 2: Copy and Run Setup Cells

### Cell 1: Install PepDesign

```python
# Clone PepDesign
!git clone https://github.com/duyjimmypham/pepdesign.git
%cd pepdesign

# Install dependencies
!pip install -q pydantic biopython pandas pandarallel pdbfixer openmm

print("✅ PepDesign installed")
```

**Run this cell** (Shift+Enter)

---

### Cell 2: Install ProteinMPNN

```python
# Clone ProteinMPNN
!git clone https://github.com/dauparas/ProteinMPNN.git /content/ProteinMPNN
%cd /content/ProteinMPNN

# Download model weights (auto-downloads ~50MB)
!mkdir -p ca_model_weights
!wget -q https://github.com/dauparas/ProteinMPNN/raw/main/ca_model_weights/v_48_020.pt \
    -O ca_model_weights/v_48_020.pt

print("✅ ProteinMPNN ready")
# Verify
!ls -lh ca_model_weights/v_48_020.pt
```

**Run this cell**

---

### Cell 3: Create Test Target

```python
# Create a simple test PDB file
test_pdb = """
ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00  0.00           N
ATOM      2  CA  ALA A   1      11.000  10.000  10.000  1.00  0.00           C
ATOM      3  C   ALA A   1      11.500  11.000  10.000  1.00  0.00           C
ATOM      4  O   ALA A   1      11.000  12.000  10.000  1.00  0.00           O
END
"""

with open('/content/test_target.pdb', 'w') as f:
    f.write(test_pdb)

print("✅ Test target created")
```

**Run this cell**

---

### Cell 4: Run PepDesign with REAL ProteinMPNN

```python
import sys
sys.path.append('/content/pepdesign')

from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import (
    PipelineConfig, GlobalConfig, TargetConfig,
    BackboneConfig, DesignConfig, ScoringConfig
)

# Configure pipeline
config = PipelineConfig(
    global_settings=GlobalConfig(
        output_dir="/content/output",
        seed=42
    ),
    target=TargetConfig(
        pdb_path="/content/test_target.pdb",
        mode="de_novo",
        target_chain="A",
        binding_site_residues=[1]
    ),
    backbone=BackboneConfig(
        generator_type="stub",  # Generates toy backbones
        num_backbones=2,        # Small for testing
        peptide_length=8
    ),
    design=DesignConfig(
        designer_type="protein_mpnn",  # ✅ REAL ProteinMPNN!
        num_sequences_per_backbone=3
    ),
    scoring=ScoringConfig()
)

# Run pipeline
print("Running pipeline with REAL ProteinMPNN...")
pipeline = PepDesignPipeline(config)
pipeline.run()

print("\n" + "="*50)
print("✅ DONE! Using real ProteinMPNN for sequence design")
print("="*50)
```

**Run this cell** - This will take ~2-3 minutes

---

### Cell 5: View Results

```python
import pandas as pd

# Load results
df = pd.read_csv('/content/output/ranking/ranked.csv')

print("Top Designed Sequences:")
print(df[['design_id', 'peptide_seq', 'composite_score']].head())

# Download results
!zip -r results.zip /content/output/
from google.colab import files
files.download('results.zip')
```

**Run this cell**

---

## What You'll See:

When Cell 4 runs, look for these messages:

```
[ProteinMPNN] Using Google Colab environment  ← REAL TOOL!
[ProteinMPNNDesigner] Designing sequences for 2 backbones...
```

**NOT:**

```
[MockRunner] Simulated...  ← This means stub mode
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'google.colab'"

**Solution**: You're not in Colab. Make sure you're at colab.research.google.com

### "ProteinMPNN not found"

**Solution**: Make sure Cell 2 ran successfully

```python
# Check installation
!ls -lh /content/ProteinMPNN/ca_model_weights/v_48_020.pt
```

### Out of memory

**Solution**: Reduce batch sizes in Cell 4:

```python
backbone=BackboneConfig(num_backbones=1),  # Reduce to 1
design=DesignConfig(num_sequences_per_backbone=2)  # Reduce to 2
```

---

## Next Steps

Once this works:

1. ✅ Upload your own target PDB
2. ✅ Adjust binding site residues
3. ✅ Increase num_backbones and num_sequences
4. ✅ Add AlphaFold3 for structure prediction (requires model params)

**You're now using real AI tools for peptide design! 🎉**
