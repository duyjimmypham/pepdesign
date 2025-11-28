"""
Integration test for structure prediction (Phase 2).
"""
import os
import shutil
from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import PipelineConfig, GlobalConfig, TargetConfig, BackboneConfig, DesignConfig, ScoringConfig, PredictionConfig

def test_prediction_integration():
    print("Testing Structure Prediction Integration...")
    
    output_dir = "test_prediction_output"
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
        
        # Test with AlphaFold2
        print("\n[Test 1] AlphaFold2 Prediction")
        config_af2 = PipelineConfig(
            global_settings=GlobalConfig(output_dir=output_dir + "/af2", seed=42),
            target=TargetConfig(pdb_path=test_pdb, mode="de_novo", target_chain="A", binding_site_residues=[1]),
            backbone=BackboneConfig(generator_type="stub", num_backbones=1, peptide_length=5),
            design=DesignConfig(designer_type="stub", num_sequences_per_backbone=2),
            scoring=ScoringConfig(),
            prediction=PredictionConfig(predictor_type="alphafold2", top_n=2, num_models=1)
        )
        pipeline_af2 = PepDesignPipeline(config_af2)
        pipeline_af2.run()
        
        # Verify outputs
        assert os.path.exists(os.path.join(output_dir, "af2/predictions"))
        print("  ✓ AlphaFold2 prediction ran (Mocked)")

        # Test with Chai-1
        print("\n[Test 2] Chai-1 Prediction")
        config_chai = PipelineConfig(
            global_settings=GlobalConfig(output_dir=output_dir + "/chai", seed=42),
            target=TargetConfig(pdb_path=test_pdb, mode="de_novo", target_chain="A", binding_site_residues=[1]),
            backbone=BackboneConfig(generator_type="stub", num_backbones=1, peptide_length=5),
            design=DesignConfig(designer_type="stub", num_sequences_per_backbone=2),
            scoring=ScoringConfig(),
            prediction=PredictionConfig(predictor_type="chai1", top_n=2, num_models=1)
        )
        pipeline_chai = PepDesignPipeline(config_chai)
        pipeline_chai.run()
        
        assert os.path.exists(os.path.join(output_dir, "chai/predictions"))
        print("  ✓ Chai-1 prediction ran (Mocked)")

        # Test with no prediction
        print("\n[Test 3] No Prediction")
        config_none = PipelineConfig(
            global_settings=GlobalConfig(output_dir=output_dir + "/none", seed=42),
            target=TargetConfig(pdb_path=test_pdb, mode="de_novo", target_chain="A", binding_site_residues=[1]),
            backbone=BackboneConfig(generator_type="stub", num_backbones=1, peptide_length=5),
            design=DesignConfig(designer_type="stub", num_sequences_per_backbone=2),
            scoring=ScoringConfig(),
            prediction=PredictionConfig(predictor_type="none")
        )
        pipeline_none = PepDesignPipeline(config_none)
        pipeline_none.run()
        
        # Should not have predictions directory
        assert not os.path.exists(os.path.join(output_dir, "none/predictions")) or \
               len(os.listdir(os.path.join(output_dir, "none/predictions"))) == 0
        print("  ✓ Skipped prediction")
    
    print("\n✅ Structure Prediction Verification Passed!")

if __name__ == "__main__":
    test_prediction_integration()
