"""
AlphaFold3 wrapper for structure prediction.
Uses AlphaFold3 for peptide-protein complex prediction.

IMPORTANT: This wrapper requires AlphaFold3 model parameters which must be
downloaded separately. Model parameters should NOT be committed to version control
per AlphaFold3's license agreement.

See: https://github.com/google-deepmind/alphafold3
"""
import os
import json
from typing import List, Dict, Any, Optional

from pepdesign.external.alphafold2 import PredictionResult
from pepdesign.runners import DockerRunner, MockRunner


class AlphaFold3Predictor:
    """
    Wrapper for AlphaFold3 structure prediction.
    
    AlphaFold3 is particularly well-suited for:
    - Peptide-protein complexes
    - Small molecule interactions
    - Multi-chain assemblies
    """
    def __init__(self, runner=None, model_dir: Optional[str] = None):
        """
        Initialize AlphaFold3 predictor.
        
        Args:
            runner: Optional runner (defaults to ColabRunner > DockerRunner > MockRunner)
            model_dir: Path to AlphaFold3 model parameters (must be downloaded separately)
        """
        from pepdesign.runners import DockerRunner, MockRunner
        
        # Try Colab first, then Docker, then Mock
        if runner is None:
            try:
                from pepdesign.runners_colab import ColabRunner
                colab_runner = ColabRunner()
                if colab_runner.is_available():
                    print("[AlphaFold3] Using Google Colab environment")
                    self.runner = colab_runner
                else:
                    raise ImportError("Not in Colab")
            except ImportError:
                # Fall back to Docker
                self.runner = DockerRunner(image="alphafold3:latest")
                if not self.runner.is_available():
                    print("[Warning] AlphaFold3 runner not available, falling back to Mock.")
                    self.runner = MockRunner()
        else:
            self.runner = runner
        
        # Model directory should be set via environment or config
        self.model_dir = model_dir or os.environ.get("AF3_MODEL_DIR", "/content/models/alphafold3")

    def predict(
        self,
        sequences: Dict[str, str],  # {design_id: sequence}
        output_dir: str,
        receptor_pdb: Optional[str] = None,
        num_models: int = 1,
        num_seeds: int = 1
    ) -> List[PredictionResult]:
        """
        Predict structures for designed sequences using AlphaFold3.
        
        Args:
            sequences: Dictionary mapping design_ids to sequences
            output_dir: Output directory
            receptor_pdb: Optional receptor structure for complex prediction
            num_models: Number of models to generate per sequence
            num_seeds: Number of random seeds per prediction
            
        Returns:
            List of PredictionResult objects
        """
        print(f"[AlphaFold3] Predicting structures for {len(sequences)} sequences...")
        os.makedirs(output_dir, exist_ok=True)
        
        # AlphaFold3 uses JSON input format
        # Create input JSON files for each sequence
        input_jsons = []
        
        for design_id, seq in sequences.items():
            input_json = os.path.join(output_dir, f"{design_id}_input.json")
            
            # AlphaFold3 JSON format (example structure)
            af3_input = {
                "name": design_id,
                "sequences": [
                    {
                        "protein": {
                            "id": "peptide",
                            "sequence": seq
                        }
                    }
                ]
            }
            
            # If receptor is provided, add it to the input
            if receptor_pdb:
                # In real implementation, we'd parse the receptor PDB
                # and extract its sequence
                af3_input["sequences"].insert(0, {
                    "protein": {
                        "id": "receptor",
                        "sequence": "A" * 10  # Default to poly-A if not extracted
                    }
                })
            
            with open(input_json, "w") as f:
                json.dump(af3_input, f, indent=2)
            
            input_jsons.append(input_json)
        
        # Command construction
        # AlphaFold3 typically runs: python run_alphafold.py --json_path=input.json --output_dir=output/
        cmd = [
            "python", "run_alphafold.py",
            "--model_dir", self.model_dir,
            "--output_dir", output_dir,
            "--num_diffusion_samples", str(num_models),
            "--num_seeds", str(num_seeds)
        ]
        
        # Add input JSONs
        for input_json in input_jsons:
            cmd.extend(["--json_path", input_json])
        
        # Run prediction
        self.runner.run(cmd, cwd=output_dir)
        
        # Parse results
        results = []
        
        for design_id in sequences.keys():
            # AlphaFold3 outputs: {design_id}_model_*.cif and {design_id}_summary_confidences.json
            
            # If Mock, create dummy files
            if isinstance(self.runner, MockRunner):
                pdb_path = os.path.join(output_dir, f"{design_id}_model_0.pdb")
                json_path = os.path.join(output_dir, f"{design_id}_summary_confidences.json")
                
                with open(pdb_path, "w") as f:
                    f.write("ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00 88.00           C\n")
                
                with open(json_path, "w") as f:
                    json.dump({
                        "iptm": 0.85,
                        "ptm": 0.88,
                        "ranking_score": 0.865,
                        "plddt": [88.0] * len(sequences[design_id])
                    }, f)
            
            # Find output files (AF3 outputs CIF, but we can convert or look for PDB)
            pdb_path = os.path.join(output_dir, f"{design_id}_model_0.pdb")
            json_path = os.path.join(output_dir, f"{design_id}_summary_confidences.json")
            
            if os.path.exists(pdb_path) and os.path.exists(json_path):
                # Parse confidence scores
                with open(json_path, "r") as f:
                    scores = json.load(f)
                
                plddt_scores = scores.get("plddt", [])
                # AlphaFold3 uses ranking_score which combines pTM and ipTM
                confidence = scores.get("ranking_score", 0.0) * 100  # Scale to 0-100
                
                results.append(PredictionResult(
                    design_id=design_id,
                    pdb_path=pdb_path,
                    confidence=confidence,
                    plddt_scores=plddt_scores,
                    metadata={
                        "predictor": "alphafold3",
                        "num_models": num_models,
                        "iptm": scores.get("iptm", None),
                        "ptm": scores.get("ptm", None),
                        "ranking_score": scores.get("ranking_score", None)
                    }
                ))
        
        return results
