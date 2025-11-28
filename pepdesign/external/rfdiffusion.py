"""
RFdiffusion wrapper for backbone generation.
"""
import os
import json
from typing import List, Dict, Any

from pepdesign.interfaces import BackboneGenerator, BackboneResult
from pepdesign.config import BackboneConfig
from pepdesign.runners import DockerRunner, MockRunner
from pepdesign.utils import save_csv_from_dicts

class RFdiffusionGenerator(BackboneGenerator):
    """
    Wrapper for RFdiffusion using Docker.
    """
    def __init__(self, runner=None):
        from pepdesign.runners import DockerRunner, MockRunner
        
        # Try Colab first, then Docker, then Mock
        if runner is None:
            try:
                from pepdesign.runners_colab import ColabRunner
                colab_runner = ColabRunner()
                if colab_runner.is_available():
                    print("[RFdiffusion] Using Google Colab environment")
                    self.runner = colab_runner
                else:
                    raise ImportError("Not in Colab")
            except ImportError:
                # Fall back to Docker
                self.runner = DockerRunner(image="rfdiffusion:latest")
                if not self.runner.is_available():
                    print("[Warning] RFdiffusion runner not available, falling back to Mock.")
                    self.runner = MockRunner()
        else:
            self.runner = runner

    def generate(
        self,
        target_pdb: str,
        binding_site_data: Dict[str, Any],
        output_dir: str,
        config: BackboneConfig,
        existing_peptide_data: Dict[str, Any] = None
    ) -> List[BackboneResult]:
        
        print(f"[RFdiffusion] Generating {config.num_backbones} backbones...")
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Prepare Inference Config/Command
        # RFdiffusion typically takes a 'contigmap'
        
        # Calculate contig string
        # Example: [10-100/A] [10-20] (Target chain A residues 10-100, then 10-20 residue peptide)
        
        # For simplicity in this wrapper, we'll assume we want to fix the target and diffuse the binder.
        # We need to know the target chain length or residues.
        # Since we have the cleaned PDB, we can inspect it or assume the user provided info.
        
        # Let's construct a simple contig: "['A1-end', '5-15']" 
        # meaning: Keep chain A fixed, generate a binder of length 5-15.
        
        peptide_length = config.peptide_length or 10
        # If we have a range, we could use it, but config has single int. 
        # Let's say length +/- 0? Or just length.
        
        contig = f"['A1-1000', '{peptide_length}-{peptide_length}']" # Simplified: Assume A is < 1000 residues
        
        # In a real implementation, we would parse the PDB to get exact residue ranges for the target.
        
        # Hotspot residues?
        # binding_site_data['residue_indices'] are the hotspots on the target.
        # RFdiffusion syntax: "ppi.hotspot_res=[A10,A23,...]"
        
        hotspots = []
        if binding_site_data.get("residue_indices"):
            # format: A10,A11...
            chain = binding_site_data.get("chain_id", "A")
            hotspots = [f"{chain}{r}" for r in binding_site_data["residue_indices"]]
        
        hotspot_str = f"ppi.hotspot_res=[{','.join(hotspots)}]" if hotspots else ""
        
        output_prefix = os.path.join(output_dir, "rfdiffusion_out")
        
        cmd = [
            "python", "scripts/run_inference.py",
            f"inference.input_pdb={target_pdb}",
            f"inference.output_prefix={output_prefix}",
            f"contigmap.contigs={contig}",
            f"inference.num_designs={config.num_backbones}",
        ]
        
        if hotspot_str:
            cmd.append(hotspot_str)
            
        # Run
        # We need to mount the input PDB directory and output directory
        # DockerRunner handles mounts if we configure it, but here we passed the runner in __init__.
        # If it's a DockerRunner, we might need to adjust paths to be container-relative.
        # For this MVP, let's assume the runner handles basic execution or is Mock.
        
        # If using DockerRunner, we should probably instantiate it here with specific mounts
        # or have a more sophisticated path mapping system.
        # For now, let's rely on the MockRunner or a smart LocalRunner.
        
        self.runner.run(cmd, cwd=output_dir)
        
        # Collect results
        results = []
        # RFdiffusion outputs: output_prefix_0.pdb, output_prefix_1.pdb...
        
        for i in range(config.num_backbones):
            pdb_name = f"rfdiffusion_out_{i}.pdb"
            pdb_path = os.path.join(output_dir, pdb_name)
            
            # If Mock, generate a dummy file
            if isinstance(self.runner, MockRunner):
                with open(pdb_path, "w") as f:
                    # Write valid PDB line
                    f.write("ATOM      1  CA  ALA B   1       0.000   0.000   0.000  1.00  0.00           C\n")
            
            if os.path.exists(pdb_path):
                results.append(BackboneResult(
                    backbone_id=f"rfdiffusion_{i}",
                    pdb_path=pdb_path,
                    peptide_chain_id="B", # RFdiffusion usually makes chain B the binder
                    metadata={"mode": "rfdiffusion", "contig": contig}
                ))
                
        return results
