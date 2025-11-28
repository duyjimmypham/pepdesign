"""
Integration test for AlphaFold3 prediction.
"""
import os
import shutil
from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import PipelineConfig, GlobalConfig, TargetConfig, BackboneConfig, DesignConfig, ScoringConfig, PredictionConfig

def test_alphafold3_integration():
    print("Testing AlphaFold3 Integration...")
    
    output_dir = "test_af3_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    test_pdb = "tests/dummy_test.pdb"
    if not os.path.exists(test_pdb):
        with open(test_pdb, "w") as f:
            f.write("ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00  0.00           N\n")

    # Mock DockerRunner
    from unittest.mock import patch
    from pepdesign.runners import MockRunner
    
    with patch('pepdesign.runners.DockerRunner') as MockDocker:
        MockDocker.side_effect = lambda *args, **kwargs: MockRunner()
        
        # Test with AlphaFold3
        print("\n[Test 1] AlphaFold3 Prediction")
        config_af3 = PipelineConfig(
            global_settings=GlobalConfig(output_dir=output_dir, seed=42),
            target=TargetConfig(pdb_path=test_pdb, mode="de_novo", target_chain="A", binding_site_residues=[1]),
            backbone=BackboneConfig(generator_type="stub", num_backbones=1, peptide_length=5),
            design=DesignConfig(designer_type="stub", num_sequences_per_backbone=2),
            scoring=ScoringConfig(),
            prediction=PredictionConfig(
                predictor_type="alphafold3",
                top_n=2,
                num_models=1,
                model_dir="models/alphafold3"  # Will use mock, so path doesn't matter
            )
        )
        pipeline_af3 = PepDesignPipeline(config_af3)
        pipeline_af3.run()
        
        # Verify outputs
        assert os.path.exists(os.path.join(output_dir, "predictions"))
        print("  ✓ AlphaFold3 prediction ran (Mocked)")
        
        # Check that predictions.csv was created
        predictions_csv = os.path.join(output_dir, "predictions/predictions.csv")
        if os.path.exists(predictions_csv):
            import pandas as pd
            df = pd.read_csv(predictions_csv)
            print(f"  ✓ Generated {len(df)} predictions")
            # Verify AlphaFold3-specific metadata
            assert df.iloc[0]['predictor'] == 'alphafold3'
            assert 'ranking_score' in df.columns or 'ranking_score' in df.iloc[0].to_dict()
            print("  ✓ AlphaFold3 metadata verified")
    
    print("\n✅ AlphaFold3 Verification Passed!")

if __name__ == "__main__":
    test_alphafold3_integration()
