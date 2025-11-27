# Changelog

## [0.2.0] - 2025-11-27

### Added

- Pipeline orchestration class (`PepDesignPipeline`)
- Pydantic configuration models
- Abstract base classes for extensibility
- ProteinMPNN wrapper with Docker support
- Parallel scoring with pandarallel
- Interactive HTML reports with 3Dmol.js

### Changed

- **Breaking**: Refactored to object-oriented architecture
- **Breaking**: Config now uses Pydantic instead of JSON
- Improved error handling and validation
- Simplified example scripts

### Removed

- Legacy functional implementation (moved to `archive/`)

### Fixed

- Path resolution in HTML reports
- jQuery loading order
- Cross-platform PDB handling

## [0.1.0] - 2024

Initial release with basic workflow:

- Target preparation
- Stub backends
- Physicochemical scoring
- CSV output

## Migration (v0.1 → v0.2)

**Before:**

```python
from pepdesign.modules import prepare_target
import json
config = json.load(open('config.json'))
prepare_target(**config)
```

**After:**

```python
from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import TargetConfig

pipeline = PepDesignPipeline(output_dir="output")
pipeline.prepare_target(
    pdb_path="target.pdb",
    config=TargetConfig(mode="de_novo", target_chain="A")
)
```
