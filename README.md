# PepDesign - Modular Peptide Design Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modular, extensible Python pipeline for **de novo** peptide design and optimization using computational biology tools.

---

## Overview

PepDesign is a research-grade pipeline for designing macrocyclic peptide binders targeting specific protein binding sites. The pipeline integrates state-of-the-art computational tools while maintaining a clean, modular architecture that allows easy extension and customization.

### Key Features

- **Modular Architecture** - Each step is independent and swappable
- **Two Design Modes** - De novo design or optimization of existing peptides
- **Extensible Backend** - Easy integration of new tools (RFdiffusion, ProteinMPNN, AlphaFold)
- **Physicochemical Scoring** - Built-in filters for charge, hydrophobicity, aggregation
- **Macrocycle Support** - Specialized handling for cyclic peptides

---

## Pipeline Architecture

```
┌─────────────────┐
│ Target Prep     │  Clean PDB, identify binding site
└────────┬────────┘
         ↓
┌─────────────────┐
│ Backbone Gen    │  RFdiffusion/RFpeptides (stub)
└────────┬────────┘
         ↓
┌─────────────────┐
│ Sequence Design │  ProteinMPNN (stub)
└────────┬────────┘
         ↓
┌─────────────────┐
│ Scoring         │  Physicochemical properties
└────────┬────────┘
         ↓
┌─────────────────┐
│ Ranking         │  Filter and rank candidates
└─────────────────┘
```

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pepdesign.git
cd pepdesign

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### 1. Prepare Target Structure

```python
from pepdesign.modules.prepare_target import prepare_target

prepare_target(
    pdb_path="target.pdb",
    output_dir="output/target",
    mode="de_novo",
    target_chain="A",
    binding_site_residues=[45, 46, 89, 90, 120],
)
```

#### 2. Generate Backbones

```python
from pepdesign.modules.generate_backbones import generate_backbones

generate_backbones(
    target_pdb="output/target/target_clean.pdb",
    binding_site_json="output/target/binding_site.json",
    output_dir="output/backbones",
    num_backbones=10,
    peptide_length=8,
    mode="stub",  # Use "rfpeptides" for real RFdiffusion
)
```

#### 3. Design Sequences

```python
from pepdesign.modules.design_sequences import design_sequences

design_sequences(
    backbones_dir="output/backbones",
    output_csv="output/sequences.csv",
    mode="de_novo",
    num_sequences_per_backbone=5,
)
```

#### 4. Score and Filter

```python
from pepdesign.modules.score_sequences import score_sequences

score_sequences(
    sequences_csv="output/sequences.csv",
    output_csv="output/scored.csv",
    ph=7.4,
    charge_min=-3.0,
    charge_max=5.0,
    max_hydrophobic_fraction=0.6,
    max_cys_count=2,
)
```

---

## Examples

### 1. MDM2-p53 Optimization (Optimize Existing)

Demonstrates optimizing an existing binder with reference-aware scoring.

```bash
cd examples/mdm2_p53
python run_full_local.py
```

### 2. Toy De Novo Design

Demonstrates designing a binder from scratch for a target pocket.

```bash
cd examples/toy_denovo
python run_full_local.py
```

---

## Running the Full Local Pipeline (Stub Mode)

For a complete end-to-end example using lightweight CPU-only stub backends:

```bash
cd examples/mdm2_p53
python run_full_local.py
```

This runs the complete pipeline:

1. Target preparation
2. Backbone generation
3. Sequence design (stub backend)
4. Physicochemical scoring
5. Ranking

**No GPU or external tools required.** The stub backend is perfect for:

- Testing the pipeline
- Developing new features
- Learning the workflow
- Prototyping designs

For real ProteinMPNN integration, use `backend="local"` or `backend="colab"` (future implementation).

---

## Project Structure

```
pepdesign/
├── modules/                    # Core pipeline modules
│   ├── prepare_target.py      # Target structure preparation
│   ├── generate_backbones.py  # Backbone generation
│   ├── design_sequences.py    # Sequence design
│   └── score_sequences.py     # Physicochemical scoring
├── external/                   # External tool wrappers
│   ├── rfpeptides.py          # RFdiffusion/RFpeptides stub
│   └── protein_mpnn.py        # ProteinMPNN stub
└── utils/                      # Shared utilities
    └── pdb_utils.py           # PDB I/O helpers

tests/                          # Unit tests
├── test_prepare.py
├── test_backbone.py
├── test_sequences.py
└── test_scoring.py
```

---

## Design Modes

### De Novo Design

Design peptides from scratch for a given binding site:

- Specify binding site residues manually
- Auto-detect pocket (experimental)
- Generate diverse backbone geometries
- Sample sequence space with ProteinMPNN

### Optimization Mode

Improve existing peptide binders:

- Extract peptide from complex structure
- Identify binding site from peptide location
- Fix key residues while optimizing others
- Maintain structural constraints

---

## Scoring Metrics

The pipeline computes multiple physicochemical properties:

| Property                   | Description                                   | Filter        |
| -------------------------- | --------------------------------------------- | ------------- |
| **Net Charge**             | pH-dependent charge (Henderson-Hasselbalch)   | Min/Max range |
| **Isoelectric Point (pI)** | pH where net charge = 0                       | -             |
| **Hydrophobic Fraction**   | Percentage of hydrophobic residues (AVILMFWY) | Max threshold |
| **Aromatic Fraction**      | Percentage of aromatic residues (F, W, Y)     | -             |
| **Positive Fraction**      | Percentage of basic residues (K, R, H)        | -             |
| **Negative Fraction**      | Percentage of acidic residues (D, E)          | -             |
| **Polar Fraction**         | Percentage of polar uncharged residues        | -             |
| **Cysteine Count**         | Number of cysteines                           | Max count     |
| **Aggregation Flag**       | Detects problematic motifs (WWW, IIII, etc.)  | Boolean       |

In **optimize_existing** mode, ranking also considers similarity to the reference peptide's properties.

---

## Extending the Pipeline

### Adding a New Tool

1. Create wrapper in `external/`:

```python
# external/my_tool.py
def run_my_tool(input_pdb: str, config: dict) -> dict:
    # Your implementation
    pass
```

2. Update the corresponding module:

```python
from pepdesign.external.my_tool import run_my_tool

# Use in your pipeline step
result = run_my_tool(pdb_path, config)
```

### Custom Scoring Functions

Add new scoring functions to `score_sequences.py`:

```python
def my_custom_score(seq: str) -> float:
    # Your scoring logic
    return score
```

---

## Example Output

**Scored Sequences CSV:**

```csv
backbone_id,design_id,peptide_seq,net_charge,pI,hydrophobic_fraction,filtered_out
backbone_0,bb0_seq_0,ACDEFGHIKL,-0.99,5.25,0.40,False
backbone_0,bb0_seq_1,KKKRRRDDD,5.97,12.81,0.00,True
backbone_1,bb1_seq_0,AVILMFWY,-0.02,7.00,1.00,True
```

---

## Technology Stack

- **Python 3.10+** - Core language
- **Biopython** - PDB parsing and manipulation
- **Pandas** - Data processing and CSV handling
- **NumPy** - Numerical computations
- **RFdiffusion** - Backbone generation (external, stub)
- **ProteinMPNN** - Sequence design (external, stub)
- **AlphaFold/ColabFold** - Structure prediction (planned)

---

## Use Cases

- **Drug Discovery** - Design peptide therapeutics
- **Protein Engineering** - Create novel protein-protein interactions
- **Research** - Explore sequence-structure relationships
- **Education** - Learn computational peptide design

---

## Roadmap

- [x] Core pipeline architecture
- [x] Target preparation with binding site detection
- [x] Backbone generation (stub mode)
- [x] Sequence design (stub mode)
- [x] Physicochemical scoring and filtering
- [ ] Real RFdiffusion integration
- [ ] Real ProteinMPNN integration
- [ ] AlphaFold structure prediction
- [ ] Energy-based scoring (Rosetta/OpenMM)
- [ ] Web interface for visualization
- [ ] Docker containerization

---

## Citation

If you use this pipeline in your research, please cite:

```bibtex
@software{pepdesign2025,
  title = {PepDesign: A Modular Pipeline for Peptide Design},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/pepdesign}
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## Contact

**Your Name** - [@yourtwitter](https://twitter.com/yourtwitter) - your.email@example.com

Project Link: [https://github.com/yourusername/pepdesign](https://github.com/yourusername/pepdesign)

---

## Acknowledgments

- [RFdiffusion](https://github.com/RosettaCommons/RFdiffusion) - Backbone generation
- [ProteinMPNN](https://github.com/dauparas/ProteinMPNN) - Sequence design
- [AlphaFold](https://github.com/deepmind/alphafold) - Structure prediction
- [Biopython](https://biopython.org/) - Structural biology toolkit
