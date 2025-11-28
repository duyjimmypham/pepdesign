"""
DiffPepBuilder wrapper for backbone generation.
"""
import os
from typing import List, Dict, Any

from pepdesign.interfaces import BackboneGenerator, BackboneResult
from pepdesign.config import BackboneConfig
from pepdesign.runners import DockerRunner, MockRunner

class DiffPepBuilderGenerator(BackboneGenerator):
    """
    Wrapper for DiffPepBuilder using Docker.
    """
    def __init__(self, runner=None):
        self.runner = runner or DockerRunner(image="diffpepbuilder:latest")
        if not self.runner.is_available():
            print("[Warning] DiffPepBuilder runner not available, falling back to Mock.")
            self.runner = MockRunner()

    def generate(
        self,
        target_pdb: str,
        binding_site_data: Dict[str, Any],
        output_dir: str,
        config: BackboneConfig,
        existing_peptide_data: Dict[str, Any] = None
    ) -> List[BackboneResult]:
        
        print(f"[DiffPepBuilder] Generating {config.num_backbones} backbones...")
        os.makedirs(output_dir, exist_ok=True)
        
        # DiffPepBuilder typically takes receptor and sequence length
        peptide_length = config.peptide_length or 10
        
        # Command construction (Hypothetical based on typical diffusion models)
        # python inference.py --receptor target.pdb --len 10 --num 10 --out output/
        
        cmd = [
            "python", "inference.py",
            "--receptor", target_pdb,
            "--len", str(peptide_length),
            "--num", str(config.num_backbones),
            "--out_dir", output_dir
        ]
        
        self.runner.run(cmd, cwd=output_dir)
        
        # Collect results
        results = []
        for i in range(config.num_backbones):
            # Assume output naming convention
            pdb_name = f"generated_{i}.pdb"
            pdb_path = os.path.join(output_dir, pdb_name)
            
            # If Mock, generate a dummy file
            if isinstance(self.runner, MockRunner):
                with open(pdb_path, "w") as f:
                    # Write valid PDB line
                    f.write("ATOM      1  CA  ALA B   1       0.000   0.000   0.000  1.00  0.00           C\n")
            
            if os.path.exists(pdb_path):
                results.append(BackboneResult(
                    backbone_id=f"diffpepbuilder_{i}",
                    pdb_path=pdb_path,
                    peptide_chain_id="B", # Assumption
                    metadata={"mode": "diffpepbuilder"}
                ))
                
        return results
