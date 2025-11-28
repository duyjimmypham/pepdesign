<p align="center">
  <img src="banner.png" alt="PepDesign Banner" width="300">
</p>

# PepDesign

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A modular, production-ready pipeline for computational peptide design and optimization.**

PepDesign integrates state-of-the-art deep learning models for peptide-protein interface design, sequence optimization, and structure prediction.

---

## 🌟 Features

### Core Pipeline

- **Modular Architecture** - Swappable backends for each step
- **Two Design Modes** - De novo design or optimization of existing peptides
- **Structure Relaxation** - OpenMM-based energy minimization
- **Type-Safe Configuration** - Pydantic models for all parameters

### Backbone Generation

- **RFdiffusion** - State-of-the-art diffusion model for binder design
- **DiffPepBuilder** - Specialized peptide backbone generator
- **Stub Mode** - Fast prototyping with macrocycle generation

### Sequence Design

- **ProteinMPNN** - Deep learning sequence design
- **Constraint Support** - Fixed positions, disallowed residues
- **Batch Processing** - Parallel sequence generation

### Structure Prediction

- **AlphaFold2** - Industry-standard structure prediction (via ColabFold)
- **AlphaFold3** - Latest version with enhanced accuracy
- **Chai-1** - Fast alternative for peptide-protein complexes

### Analysis & Filtering

- **Physicochemical Properties** - Charge, hydrophobicity, pI, aromaticity
- **Custom Filters** - Configurable thresholds for all properties
- **Reference Comparison** - Target-aware scoring for optimization mode
- **Interactive Reports** - HTML reports with 3D visualization

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- CUDA 11.8+ (for GPU acceleration)
- Docker (optional, for tool integration)

### Basic Installation

```bash
git clone https://github.com/duyjimmypham/pepdesign.git
cd pepdesign
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### With OpenMM (Recommended)

```bash
pip install pdbfixer openmm
```

### Model Parameters

**⚠️ CRITICAL**: Model parameters must be downloaded separately (not included in repo).

See [docs/model_setup.md](docs/model_setup.md) for detailed instructions.

---

## 🚀 Quick Start

### Example 1: De Novo Design

```python
from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import (
    PipelineConfig, GlobalConfig, TargetConfig,
    BackboneConfig, DesignConfig, ScoringConfig, PredictionConfig
)

# Configure pipeline
config = PipelineConfig(
    global_settings=GlobalConfig(
        output_dir="output/mdm2_binder",
        seed=42
    ),
    target=TargetConfig(
        pdb_path="examples/mdm2.pdb",
        mode="de_novo",
        target_chain="A",
        binding_site_residues=[25, 26, 29, 30, 32]  # Known hotspots
    ),
    backbone=BackboneConfig(
        generator_type="rfdiffusion",  # or "diffpepbuilder", "stub"
        num_backbones=10,
        peptide_length=12
    ),
    design=DesignConfig(
        designer_type="protein_mpnn",  # or "stub"
        num_sequences_per_backbone=5
    ),
    scoring=ScoringConfig(
        charge_min=-2.0,
        charge_max=2.0,
        max_hydrophobic_fraction=0.6
    ),
    prediction=PredictionConfig(
        predictor_type="alphafold3",  # or "alphafold2", "chai1", "none"
        top_n=5,
        num_models=1,
        model_dir="models/alphafold3"
    )
)

# Run pipeline
pipeline = PepDesignPipeline(config)
pipeline.run()

# Results in output/mdm2_binder/
# - report.html (interactive 3D visualization)
# - ranking/ranked.csv (top designs)
# - predictions/ (predicted structures)
```

### Example 2: Optimize Existing Peptide

```python
config = PipelineConfig(
    global_settings=GlobalConfig(output_dir="output/p53_optimization"),
    target=TargetConfig(
        pdb_path="examples/mdm2_p53_complex.pdb",
        mode="optimize_existing",
        target_chain="A",  # MDM2
        peptide_chain="B"  # p53 peptide
    ),
    backbone=BackboneConfig(
        generator_type="stub",  # Perturb existing geometry
        num_backbones=20
    ),
    design=DesignConfig(
        designer_type="protein_mpnn",
        num_sequences_per_backbone=10
    ),
    scoring=ScoringConfig(
        # Filters relative to reference peptide
    )
)

pipeline = PepDesignPipeline(config)
pipeline.run()
```

---

## 📋 Pipeline Steps

1. **Target Preparation**

   - Clean PDB structure
   - Detect/specify binding site
   - OpenMM relaxation (optional)
   - Extract reference peptide (optimization mode)

2. **Backbone Generation**

   - RFdiffusion: AI-designed binders
   - DiffPepBuilder: Peptide-specific generation
   - Stub: Macrocycle or perturbation

3. **Sequence Design**

   - ProteinMPNN: Deep learning design
   - Constraint handling
   - Batch processing

4. **Scoring & Filtering**

   - Physicochemical properties
   - Custom thresholds
   - Reference comparison

5. **Ranking**

   - Composite scoring
   - Top-N selection

6. **Structure Prediction** (Optional)

   - AlphaFold2/3 or Chai-1
   - Confidence metrics
   - Complex prediction

7. **Reporting**
   - HTML with 3D visualization
   - Downloadable CSVs
   - Structure files

---

## 🐳 Docker Usage

### Building Docker Images

```bash
# Build all images
./scripts/build_docker_images.sh

# Or build individually
docker build -t rfdiffusion:latest -f docker/rfdiffusion/Dockerfile .
docker build -t proteinmpnn:latest -f docker/proteinmpnn/Dockerfile .
```

### Running with Docker Compose

```bash
docker-compose up
```

See [docs/docker_setup.md](docs/docker_setup.md) for details.

---

## 📚 Documentation

- [Model Setup Guide](docs/model_setup.md) - Downloading model parameters
- [Docker Setup](docs/docker_setup.md) - Container configuration
- [API Reference](docs/api_reference.md) - Detailed module documentation
- [Examples](examples/) - Complete workflows

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/test_phase1.py  # Core architecture
pytest tests/test_generators.py  # RFdiffusion, DiffPepBuilder
pytest tests/test_protein_mpnn.py  # ProteinMPNN
pytest tests/test_predictions.py  # AlphaFold2, Chai-1
pytest tests/test_alphafold3.py  # AlphaFold3
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

**Note**: External tools (RFdiffusion, ProteinMPNN, AlphaFold, etc.) have their own licenses. Model parameters must be obtained separately per their respective terms of use.

---

## 📖 Citation

If you use PepDesign in your research, please cite:

```bibtex
@software{pepdesign2024,
  title={PepDesign: A Modular Pipeline for Computational Peptide Design},
  author={Pham, Jimmy Duy},
  year={2024},
  url={https://github.com/duyjimmypham/pepdesign}
}
```

---

## 🙏 Acknowledgements

PepDesign integrates the following tools:

- [RFdiffusion](https://github.com/RosettaCommons/RFdiffusion) - Watson et al., Nature 2023
- [DiffPepBuilder](https://github.com/YuzheWangPKU/DiffPepBuilder) - Wang et al.
- [ProteinMPNN](https://github.com/dauparas/ProteinMPNN) - Dauparas et al., Science 2022
- [AlphaFold2](https://github.com/deepmind/alphafold) - Jumper et al., Nature 2021
- [AlphaFold3](https://github.com/google-deepmind/alphafold3) - Abramson et al., Nature 2024
- [Chai-1](https://github.com/chaidiscovery/chai-lab) - Chai Discovery
- [OpenMM](http://openmm.org/) - Eastman et al., JCTC 2013

---

## 📧 Contact

- **Author**: Jimmy Duy Pham
- **GitHub**: [@duyjimmypham](https://github.com/duyjimmypham)
- **Issues**: [GitHub Issues](https://github.com/duyjimmypham/pepdesign/issues)

---

**Built with ❤️ for the computational biology community**
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
├── target/ # Cleaned PDB and binding site info
├── backbones/ # Generated backbone structures
├── sequences/ # Raw sequence designs
├── scoring/ # Scored with physicochemical properties
├── ranking/ # Final ranked candidates
└── report.html # Interactive 3D visualization

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
├── modules/ # Core pipeline steps
├── external/ # Tool wrappers (ProteinMPNN, RFdiffusion)
├── utils/ # Shared utilities
├── config.py # Pydantic configuration
├── interfaces.py # Abstract base classes
├── pipeline.py # Main orchestration
└── reporting.py # HTML report generation

````

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
````

## License

MIT License - see [LICENSE](LICENSE) for details.
