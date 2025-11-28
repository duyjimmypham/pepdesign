"""
Structure prediction module.
Predicts 3D structures for designed sequences using AlphaFold2 or Chai-1.
"""
import os
import pandas as pd
from typing import List, Dict, Any

from pepdesign.config import PredictionConfig
from pepdesign.external.alphafold2 import PredictionResult
from pepdesign.utils import save_csv


class StructurePredictor:
    """Base class for structure predictors."""
    def predict(self, sequences: Dict[str, str], output_dir: str, **kwargs) -> List[PredictionResult]:
        raise NotImplementedError


def get_predictor(config: PredictionConfig) -> StructurePredictor:
    """Factory function to get structure predictor."""
    if config.predictor_type == "none":
        return NullPredictor()
    elif config.predictor_type == "alphafold2":
        from pepdesign.external.alphafold2 import AlphaFold2Predictor
        return AlphaFold2Predictor()
    elif config.predictor_type == "alphafold3":
        from pepdesign.external.alphafold3 import AlphaFold3Predictor
        return AlphaFold3Predictor(model_dir=config.model_dir)
    elif config.predictor_type == "chai1":
        from pepdesign.external.chai1 import Chai1Predictor
        return Chai1Predictor()
    else:
        raise ValueError(f"Unknown predictor type: {config.predictor_type}")


class NullPredictor(StructurePredictor):
    """Null predictor that does nothing."""
    def predict(self, sequences: Dict[str, str], output_dir: str, **kwargs) -> List[PredictionResult]:
        print("[NullPredictor] Skipping structure prediction.")
        return []


def predict_structures(
    ranked_csv: str,
    output_dir: str,
    config: PredictionConfig,
    target_pdb: str = None
) -> str:
    """
    Predict structures for top-ranked sequences.
    
    Args:
        ranked_csv: Path to ranked sequences CSV
        output_dir: Output directory for predictions
        config: Prediction configuration
        target_pdb: Optional target PDB for template/complex prediction
        
    Returns:
        Path to predictions CSV
    """
    print(f"\n[Step 6] Predicting Structures...")
    os.makedirs(output_dir, exist_ok=True)
    
    # Load ranked sequences
    df = pd.read_csv(ranked_csv)
    
    # Filter to passing sequences
    if 'passes_filters' in df.columns:
        df = df[df['passes_filters'] == True]
    
    # Take top N
    df = df.head(config.top_n)
    
    if len(df) == 0:
        print("  [Warning] No sequences to predict.")
        return None
    
    print(f"  Predicting structures for top {len(df)} sequences...")
    
    # Prepare sequences dict
    sequences = {
        row['design_id']: row['peptide_seq']
        for _, row in df.iterrows()
    }
    
    # Get predictor
    predictor = get_predictor(config)
    
    # Run prediction
    prediction_kwargs = {
        "num_models": config.num_models,
    }
    
    if config.predictor_type == "alphafold2":
        prediction_kwargs["use_templates"] = config.use_templates
        if target_pdb and config.use_templates:
            prediction_kwargs["template_pdb"] = target_pdb
    elif config.predictor_type == "alphafold3":
        if target_pdb:
            prediction_kwargs["receptor_pdb"] = target_pdb
        prediction_kwargs["num_seeds"] = 1  # Can be configurable
    elif config.predictor_type == "chai1":
        if target_pdb:
            prediction_kwargs["receptor_pdb"] = target_pdb
    
    results = predictor.predict(sequences, output_dir, **prediction_kwargs)
    
    # Save results
    if results:
        prediction_data = []
        for r in results:
            prediction_data.append({
                "design_id": r.design_id,
                "predicted_pdb": r.pdb_path,
                "mean_plddt": r.confidence,
                **r.metadata
            })
        
        predictions_csv = os.path.join(output_dir, "predictions.csv")
        save_csv(pd.DataFrame(prediction_data), predictions_csv)
        
        print(f"  [PredictStructures] Wrote {len(results)} predictions to {predictions_csv}")
        print(f"    - Mean confidence: {sum(r.confidence for r in results) / len(results):.2f}")
        
        return predictions_csv
    
    return None
