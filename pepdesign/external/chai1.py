"""
Chai-1 wrapper for structure prediction.
Chai-1 is a faster alternative to AlphaFold2 for peptide-protein complexes.
"""
import os
import json
from typing import List, Dict, Any, Optional

from pepdesign.external.alphafold2 import PredictionResult
from pepdesign.runners import DockerRunner, MockRunner


class Chai1Predictor:
    """
    Wrapper for Chai-1 structure prediction.
    """
    def __init__(self, runner=None):
        self.runner = runner or DockerRunner(image="chai1:latest")
        if not self.runner.is_available():
            print("[Warning] Chai-1 runner not available, falling back to Mock.")
            self.runner = MockRunner()

    def predict(
        self,
        sequences: Dict[str, str],  # {design_id: sequence}
        output_dir: str,
        receptor_pdb: Optional[str] = None,
        num_models: int = 1
    ) -> List[PredictionResult]:
        """
        Predict structures for designed sequences.
        
        Args:
            sequences: Dictionary mapping design_ids to sequences
            output_dir: Output directory
            receptor_pdb: Optional receptor structure for complex prediction
            num_models: Number of models to generate per sequence
            
        Returns:
            List of PredictionResult objects
        """
        print(f"[Chai-1] Predicting structures for {len(sequences)} sequences...")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create input JSON for Chai-1
        input_json = os.path.join(output_dir, "input.json")
        input_data = []
        
        for design_id, seq in sequences.items():
            entry = {
                "id": design_id,
                "peptide_sequence": seq
            }
            if receptor_pdb:
                entry["receptor_pdb"] = receptor_pdb
            input_data.append(entry)
        
        with open(input_json, "w") as f:
            json.dump(input_data, f)
        
        # Command construction
        # Hypothetical Chai-1 command
        cmd = [
            "python", "run_inference.py",
            "--input", input_json,
            "--output", output_dir,
            "--num_models", str(num_models)
        ]
        
        # Run prediction
        self.runner.run(cmd, cwd=output_dir)
        
        # Parse results
        results = []
        
        for design_id in sequences.keys():
            # Chai-1 outputs: {design_id}_model_0.pdb and {design_id}_scores.json
            
            # If Mock, create dummy files
            if isinstance(self.runner, MockRunner):
                pdb_path = os.path.join(output_dir, f"{design_id}_model_0.pdb")
                json_path = os.path.join(output_dir, f"{design_id}_scores.json")
                
                with open(pdb_path, "w") as f:
                    f.write("ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00 85.00           C\n")
                
                with open(json_path, "w") as f:
                    json.dump({
                        "confidence": 85.0,
                        "plddt": [85.0] * len(sequences[design_id])
                    }, f)
            
            # Find output files
            pdb_path = os.path.join(output_dir, f"{design_id}_model_0.pdb")
            json_path = os.path.join(output_dir, f"{design_id}_scores.json")
            
            if os.path.exists(pdb_path) and os.path.exists(json_path):
                # Parse scores
                with open(json_path, "r") as f:
                    scores = json.load(f)
                
                confidence = scores.get("confidence", 0.0)
                plddt_scores = scores.get("plddt", [])
                
                results.append(PredictionResult(
                    design_id=design_id,
                    pdb_path=pdb_path,
                    confidence=confidence,
                    plddt_scores=plddt_scores,
                    metadata={
                        "predictor": "chai1",
                        "num_models": num_models
                    }
                ))
        
        return results
