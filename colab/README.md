# ProteinMPNN Colab Template

This directory will contain Colab notebooks for running ProteinMPNN on GPU.

**Status**: Stub only — content will be added later.

## Future Implementation

The Colab notebook will:

1. Install ProteinMPNN dependencies
2. Upload backbone PDBs from local pipeline
3. Run ProteinMPNN with constraints
4. Download sequences.csv for local scoring/ranking

## Usage

```bash
# 1. Run local pipeline to generate backbones
cd examples/mdm2_p53
python run_full_local.py  # Stop after step 2

# 2. Upload backbones to Colab
# 3. Run ProteinMPNN notebook
# 4. Download sequences.csv
# 5. Continue local pipeline from step 4 (scoring)
```

## Placeholder

The actual notebook `proteinmpnn_colab_template.ipynb` will be added in a future update.
For now, use the stub backend for local testing.
