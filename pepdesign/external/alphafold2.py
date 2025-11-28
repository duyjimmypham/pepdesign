"""
AlphaFold2 wrapper for structure prediction.
Uses ColabFold for simplified AlphaFold2 predictions.
"""
import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from pepdesign.runners import DockerRunner, MockRunner


@dataclass
class PredictionResult:
    """Result from structure prediction."""
    design_id: str
    pdb_path: str
    confidence: float  # mean pLDDT
    plddt_scores: List[float]  # per-residue pLDDT
    pae_path: Optional[str] = None  # Predicted Aligned Error matrix
    metadata: Dict[str, Any] = None


class AlphaFold2Predictor:
    """
    Wrapper for AlphaFold2/ColabFold structure prediction.
    """
    def __init__(self, runner=None):
        self.runner = runner or DockerRunner(image="colabfold:latest")
        if not self.runner.is_available():
            print("[Warning] AlphaFold2 runner not available, falling back to Mock.")
            self.runner = MockRunner()

    def predict(
        self,
        sequences: Dict[str, str],  # {design_id: sequence}
        output_dir: str,
        template_pdb: Optional[str] = None,
        use_templates: bool = False,
        num_models: int = 1
    ) -> List[PredictionResult]:
        """
        Predict structures for designed sequences.
        
        Args:
            sequences: Dictionary mapping design_ids to sequences
            output_dir: Output directory
            template_pdb: Optional template structure
            use_templates: Whether to use template-based modeling
            num_models: Number of models to generate per sequence
            
        Returns:
            List of PredictionResult objects
        """
        print(f"[AlphaFold2] Predicting structures for {len(sequences)} sequences...")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create FASTA file
        fasta_path = os.path.join(output_dir, "sequences.fasta")
        with open(fasta_path, "w") as f:
            for design_id, seq in sequences.items():
                f.write(f">{design_id}\n{seq}\n")
        
        # Command construction
        # ColabFold command: colabfold_batch input.fasta output_dir
        cmd = [
            "colabfold_batch",
            fasta_path,
            output_dir,
            "--num-models", str(num_models),
            "--amber" if not use_templates else "--use-templates"
        ]
        
        if template_pdb:
            cmd.extend(["--templates", template_pdb])
        
        # Run prediction
        self.runner.run(cmd, cwd=output_dir)
        
        # Parse results
        results = []
        
        for design_id in sequences.keys():
            # ColabFold outputs: {design_id}_relaxed_rank_001_*.pdb
            # and {design_id}_scores_rank_001_*.json
            
            pdb_pattern = f"{design_id}_relaxed_rank_001"
            json_pattern = f"{design_id}_scores_rank_001"
            
            # If Mock, create dummy files
            if isinstance(self.runner, MockRunner):
                pdb_path = os.path.join(output_dir, f"{design_id}_relaxed_rank_001.pdb")
                json_path = os.path.join(output_dir, f"{design_id}_scores_rank_001.json")
                
                with open(pdb_path, "w") as f:
                    f.write("ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00 90.00           C\n")
                
                with open(json_path, "w") as f:
                    json.dump({
                        "plddt": [90.0] * len(sequences[design_id]),
                        "mean_plddt": 90.0,
                        "ptm": 0.85
                    }, f)
            
            # Find output files
            pdb_path = None
            json_path = None
            
            for fname in os.listdir(output_dir):
                if fname.startswith(pdb_pattern) and fname.endswith(".pdb"):
                    pdb_path = os.path.join(output_dir, fname)
                if fname.startswith(json_pattern) and fname.endswith(".json"):
                    json_path = os.path.join(output_dir, fname)
            
            if pdb_path and json_path:
                # Parse scores
                with open(json_path, "r") as f:
                    scores = json.load(f)
                
                plddt_scores = scores.get("plddt", [])
                mean_plddt = scores.get("mean_plddt", sum(plddt_scores) / len(plddt_scores) if plddt_scores else 0.0)
                
                results.append(PredictionResult(
                    design_id=design_id,
                    pdb_path=pdb_path,
                    confidence=mean_plddt,
                    plddt_scores=plddt_scores,
                    metadata={
                        "predictor": "alphafold2",
                        "num_models": num_models,
                        "ptm": scores.get("ptm", None)
                    }
                ))
        
        return results
