# Model Parameters Setup Guide

## ⚠️ IMPORTANT: License Compliance

**DO NOT** commit model parameters to version control. All prediction tools have licensing restrictions that prevent redistribution of their model weights.

This guide explains how to download and configure model parameters for:

- AlphaFold2 / ColabFold
- AlphaFold3
- Chai-1
- RFdiffusion
- DiffPepBuilder
- ProteinMPNN

---

## Directory Structure

Create a `models/` directory in your project root (already excluded via `.gitignore`):

```
PepDesign/
├── models/
│   ├── alphafold2/
│   ├── alphafold3/      # Downloaded separately
│   ├── chai1/
│   ├── rfdiffusion/
│   ├── diffpepbuilder/
│   └── proteinmpnn/
└── pepdesign/
```

---

## AlphaFold3

### License

AlphaFold3 model parameters are governed by [Terms of Use](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md).

**Key restrictions:**

- Non-commercial use only
- Cannot redistribute model parameters
- Must cite original paper

### Download Instructions

1. **Register and Download** (Currently in controlled access):

   ```bash
   # Follow instructions at:
   # https://github.com/google-deepmind/alphafold3#obtaining-model-parameters
   ```

2. **Extract to models directory**:

   ```bash
   mkdir -p models/alphafold3
   # Extract downloaded weights to models/alphafold3/
   ```

3. **Set environment variable** (optional):

   ```bash
   export AF3_MODEL_DIR="/path/to/PepDesign/models/alphafold3"
   ```

4. **Configure in PepDesign**:

   ```python
   from pepdesign.config import PredictionConfig

   config = PredictionConfig(
       predictor_type="alphafold3",
       model_dir="models/alphafold3",  # Or use AF3_MODEL_DIR env var
       num_models=1
   )
   ```

---

## AlphaFold2 / ColabFold

### Download Instructions

1. **Using ColabFold (Recommended)**:

   ```bash
   # ColabFold models are smaller and faster
   setup_databases.sh models/alphafold2
   ```

2. **Or download full AlphaFold2 parameters**:
   ```bash
   bash scripts/download_alphafold_databases.sh models/alphafold2
   ```

---

## Chai-1

### Download Instructions

```bash
# Clone Chai-1 and download weights
git clone https://github.com/chaidiscovery/chai-lab.git
cd chai-lab
python scripts/download_models.py --output_dir ../models/chai1
```

---

## RFdiffusion

### Download Instructions

```bash
mkdir -p models/rfdiffusion
cd models/rfdiffusion

# Download model weights
wget https://files.ipd.uw.edu/pub/RFdiffusion/6f5902ac237024bdd0c176cb93063dc4/Base_ckpt.pt
wget https://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt
```

---

## ProteinMPNN

### Download Instructions

```bash
mkdir -p models/proteinmpnn
cd models/proteinmpnn

# Download model weights
wget https://github.com/dauparas/ProteinMPNN/raw/main/ca_model_weights/v_48_020.pt
```

---

## DiffPepBuilder

### Download Instructions

```bash
# Follow instructions at:
# https://github.com/YuzheWangPKU/DiffPepBuilder

git clone https://github.com/YuzheWangPKU/DiffPepBuilder.git
# Model weights should be in the repository or downloadable via their instructions
```

---

## Verification

### Check Model Files

```bash
# Ensure models directory is populated
ls -lh models/alphafold3/
ls -lh models/alphafold2/
ls -lh models/chai1/
ls -lh models/rfdiffusion/
ls -lh models/proteinmpnn/
```

### Verify .gitignore

```bash
# Ensure model files are ignored
git status

# You should NOT see any files under models/
# If you do, check .gitignore and run:
git rm -r --cached models/
```

---

## Environment Variables

Set these in your `.bashrc`, `.zshrc`, or before running:

```bash
export AF3_MODEL_DIR="/path/to/PepDesign/models/alphafold3"
export AF2_MODEL_DIR="/path/to/PepDesign/models/alphafold2"
export CHAI_MODEL_DIR="/path/to/PepDesign/models/chai1"
export RFDIFFUSION_MODEL_DIR="/path/to/PepDesign/models/rfdiffusion"
export PROTEINMPNN_MODEL_DIR="/path/to/PepDesign/models/proteinmpnn"
```

---

## License Summary

| Tool           | License      | Commercial Use | Redistribution         |
| -------------- | ------------ | -------------- | ---------------------- |
| AlphaFold3     | Proprietary  | ❌ No          | ❌ No                  |
| AlphaFold2     | Apache 2.0   | ✅ Yes         | ✅ Yes (with citation) |
| Chai-1         | Check repo   | ⚠️ TBD         | ⚠️ TBD                 |
| RFdiffusion    | BSD 3-Clause | ✅ Yes         | ✅ Yes                 |
| ProteinMPNN    | MIT          | ✅ Yes         | ✅ Yes                 |
| DiffPepBuilder | Check repo   | ⚠️ TBD         | ⚠️ TBD                 |

**Always check the respective repositories for the most up-to-date license information.**

---

## Questions?

- AlphaFold3: https://github.com/google-deepmind/alphafold3/issues
- General PepDesign: Open an issue in this repository
