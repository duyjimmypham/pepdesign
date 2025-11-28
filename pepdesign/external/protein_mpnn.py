"""
ProteinMPNN wrapper for sequence design.
Supports running via Docker (recommended) or local installation.
"""
import os
import json
import subprocess
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional

from pepdesign.interfaces import SequenceDesigner, DesignResult, BackboneResult
from pepdesign.config import DesignConfig
from pepdesign.utils import save_csv

class ProteinMPNNDesigner(SequenceDesigner):
    """
    Wrapper for ProteinMPNN sequence design.
    """
    
    def __init__(self, runner=None):
        from pepdesign.runners import DockerRunner, MockRunner
        
        # Try Colab first, then Docker, then Mock
        if runner is None:
            try:
                from pepdesign.runners_colab import ColabRunner
                colab_runner = ColabRunner()
                if colab_runner.is_available():
                    print("[ProteinMPNN] Using Google Colab environment")
                    self.runner = colab_runner
                else:
                    raise ImportError("Not in Colab")
            except ImportError:
                # Fall back to Docker
                self.runner = DockerRunner(image="protein_mpnn:latest")
                if not self.runner.is_available():
                    print("[Warning] ProteinMPNN runner not available, falling back to Mock.")
                    self.runner = MockRunner()
        else:
            self.runner = runner

    def design(
        self,
        backbone_results: List[BackboneResult],
        output_dir: str,
        config: DesignConfig,
        global_constraints: Dict[str, Any] = None
    ) -> List[DesignResult]:
        
        print(f"[ProteinMPNNDesigner] Designing sequences for {len(backbone_results)} backbones...")
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare input for ProteinMPNN (folder of PDBs)
        # We need to make sure all backbones are in a directory ProteinMPNN can access
        # Since we are likely running Docker, we'll map the project root.
        
        # For now, we'll assume we run ProteinMPNN on each backbone individually or in batch
        # ProteinMPNN takes a folder of PDBs or a jsonl file.
        
        # Let's prepare a JSONL file which is more robust for constraints
        jsonl_path = os.path.join(output_dir, "input_pdbs.jsonl")
        self._create_jsonl_input(backbone_results, jsonl_path, global_constraints)
        
        output_seqs_path = os.path.join(output_dir, "seqs")
        os.makedirs(output_seqs_path, exist_ok=True)
        
        # Command construction
        # docker run -v /path/to/data:/data protein_mpnn ...
        
        cmd = [
            "python", "protein_mpnn_run.py",
            "--jsonl_path", jsonl_path,
            "--out_folder", output_seqs_path,
            "--num_seq_per_target", str(config.num_sequences_per_backbone),
            "--batch_size", "1"
        ]
        
        # Run via Runner
        self.runner.run(cmd, cwd=output_dir)
        
        # Parse results
        results = []
        import random # Fallback for mock
        
        for bb in backbone_results:
            # ProteinMPNN outputs .fa files in output_seqs_path
            # Filename usually matches the 'name' in JSONL, which is bb.backbone_id
            fa_path = os.path.join(output_seqs_path, f"{bb.backbone_id}.fa")
            
            # If MockRunner, generate dummy FASTA
            from pepdesign.runners import MockRunner
            if isinstance(self.runner, MockRunner):
                with open(fa_path, "w") as f:
                    f.write(f">{bb.backbone_id}, score=1.0, global_score=1.0, fixed_chains=[], designed_chains=[B]\n")
                    f.write("ACDEFGHIKL\n") # Dummy sequence
                    for i in range(config.num_sequences_per_backbone):
                        f.write(f">{bb.backbone_id}_seq_{i}, T=0.1, score=0.5, global_score=0.5, seq_recovery=0.0\n")
                        f.write("ACDEFGHIKL\n")

            if os.path.exists(fa_path):
                # Parse FASTA
                with open(fa_path, "r") as f:
                    lines = f.readlines()
                
                # ProteinMPNN FASTA format:
                # >name, score=..., global_score=..., fixed_chains=..., designed_chains=...
                # SEQUENCE
                # >name, T=..., score=..., global_score=..., seq_recovery=...
                # SEQUENCE
                
                # First entry is usually the native/input sequence (if provided) or just header
                # Subsequent entries are designs
                
                for i in range(1, len(lines), 2): # Skip first entry (input), read pairs
                    if i+1 >= len(lines): break
                    header = lines[i].strip()
                    seq = lines[i+1].strip()
                    
                    # Parse score from header
                    # >name, T=0.1, score=0.5, ...
                    score = 0.0
                    try:
                        parts = header.split(',')
                        for p in parts:
                            if "score=" in p and "global_score" not in p: # specific score
                                score = float(p.split('=')[1])
                    except:
                        pass
                        
                    design_id = f"{bb.backbone_id}_seq_{i//2}" # approximate index
                    
                    results.append(DesignResult(
                        design_id=design_id,
                        backbone_id=bb.backbone_id,
                        sequence=seq,
                        score=score,
                        metadata={"mode": "protein_mpnn", "mpnn_score": score, "pdb_path": bb.pdb_path}
                    ))
        
        # Save results to CSV
        csv_rows = [
            {
                "design_id": r.design_id,
                "backbone_id": r.backbone_id,
                "peptide_seq": r.sequence,
                "score": r.score,
                **r.metadata
            }
            for r in results
        ]
        save_csv(pd.DataFrame(csv_rows), os.path.join(output_dir, "sequences.csv"))
        
        return results

    def _create_jsonl_input(
        self, 
        backbone_results: List[BackboneResult], 
        output_path: str,
        global_constraints: Dict[str, Any]
    ):
        """Create JSONL input file for ProteinMPNN."""
        with open(output_path, 'w') as f:
            for bb in backbone_results:
                # Create simplified JSONL entry
                entry = {
                    "name": bb.backbone_id,
                    "pdb_path": bb.pdb_path,
                    "chain_id": bb.peptide_chain_id
                    # Add constraints here
                }
                f.write(json.dumps(entry) + "\n")
