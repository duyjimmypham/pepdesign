from typing import Any, Dict, List
from .base import BackboneGeneratorModule
import random

class RFPeptidesStub(BackboneGeneratorModule):
    """
    Stub for RFpeptides backbone generation.
    Returns mock backbone data.
    """
    def generate(self, target_info: Dict[str, Any], num_backbones: int = 1) -> List[Dict[str, Any]]:
        print(f"[Backbone] Generating {num_backbones} backbones using RFpeptides stub...")
        backbones = []
        for i in range(num_backbones):
            # In a real implementation, this would run RFdiffusion/RFpeptides
            # and return paths to generated PDB backbones.
            backbones.append({
                "id": f"bb_{i}",
                "pdb_content": "ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N\n...", # Mock PDB content
                "source": "RFpeptides_stub"
            })
        return backbones
