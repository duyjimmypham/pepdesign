<p align="center">
  <img src="banner.png" alt="PepDesign Banner" width="300">
</p>

# PepDesign

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python pipeline for computational peptide design and optimization.

## Features

- Modular architecture with swappable backends
- Support for de novo design and optimization workflows
- ProteinMPNN integration (Docker or stub mode)
- Physicochemical property filtering
- Interactive 3D reports with 3Dmol.js

## Installation

```bash
git clone https://github.com/duyjimmypham/pepdesign.git
cd pepdesign
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Quick Start

```python
from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import TargetConfig, BackboneConfig, DesignConfig, ScoringConfig

# Initialize
pipeline = PepDesignPipeline(output_dir="output")

# Prepare target
pipeline.prepare_target(
    pdb_path="target.pdb",
    config=TargetConfig(mode="de_novo", target_chain="A")
)

# Generate backbones
pipeline.generate_backbones(
    config=BackboneConfig(generator_type="stub", num_backbones=5)
)

# Design sequences
pipeline.design_sequences(
    config=DesignConfig(designer_type="protein_mpnn", num_sequences=10)
)

# Score and rank
pipeline.score_and_rank(
    config=ScoringConfig(ph=7.4, charge_min=-2.0, charge_max=2.0)
)
```

See `examples/mdm2_p53/run_pipeline.py` for a complete example.

## Output Structure

```
output/
├── target/          # Cleaned PDB and binding site info
├── backbones/       # Generated backbone structures
├── sequences/       # Raw sequence designs
├── scoring/         # Scored with physicochemical properties
├── ranking/         # Final ranked candidates
└── report.html      # Interactive 3D visualization
```

## Scoring Metrics

| Metric               | Description            | Filter  |
| -------------------- | ---------------------- | ------- |
| Net Charge           | pH-dependent charge    | Min/Max |
| pI                   | Isoelectric point      | -       |
| Hydrophobic Fraction | % hydrophobic residues | Max     |
| Aggregation          | Problematic motifs     | Boolean |

## Project Structure

```
pepdesign/
├── modules/         # Core pipeline steps
├── external/        # Tool wrappers (ProteinMPNN, RFdiffusion)
├── utils/           # Shared utilities
├── config.py        # Pydantic configuration
├── interfaces.py    # Abstract base classes
├── pipeline.py      # Main orchestration
└── reporting.py     # HTML report generation
```

## Design Modes

**De Novo**: Design peptides from scratch for a target pocket.

**Optimization**: Improve existing peptide binders.

## Roadmap

- [x] Pipeline architecture (v0.2)
- [x] ProteinMPNN wrapper
- [x] Parallel scoring
- [x] HTML reports
- [ ] RFdiffusion integration
- [ ] AlphaFold prediction
- [ ] Energy-based scoring

## Citation

```bibtex
@software{pepdesign2025,
  title = {PepDesign: A Modular Pipeline for Peptide Design},
  author = {Duy Pham},
  year = {2025},
  url = {https://github.com/duyjimmypham/pepdesign}
}
```

## License

MIT License - see [LICENSE](LICENSE) for details.
