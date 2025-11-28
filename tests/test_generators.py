"""
Integration test for RFdiffusion and DiffPepBuilder (Phase 1).
"""
import os
import shutil
from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import PipelineConfig, GlobalConfig, TargetConfig, BackboneConfig, DesignConfig, ScoringConfig

def test_generators_integration():
    print("Testing Generators Integration...")
    
    output_dir = "test_generators_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    test_pdb = "tests/dummy_test.pdb"
    if not os.path.exists(test_pdb):
        with open(test_pdb, "w") as f:
            f.write("ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00  0.00           N\n")

    # Mock DockerRunner to avoid actual docker calls
    from unittest.mock import patch, MagicMock
    
    with patch('pepdesign.runners.DockerRunner') as MockDocker:
        # Setup mock instance
        mock_instance = MockDocker.return_value
        mock_instance.is_available.return_value = True
        mock_instance.run.return_value = MagicMock(returncode=0)
        
        # We also need to ensure the "output files" are created, otherwise the generator will return empty results.
        # The generators check for file existence.
        # Since we can't easily side-effect file creation from the mock runner (it just runs a command),
        # we need to side-effect the file creation OR use the MockRunner class which does that.
        
        # Actually, let's patch the generators to use MockRunner internally?
        # Or better, let's patch 'pepdesign.modules.generate_backbones.RFdiffusionGenerator' 
        # but that's hard because it's imported inside the factory.
        
        # Let's patch 'pepdesign.runners.DockerRunner' to behave like 'MockRunner'
        # But MockRunner has a specific 'run' method that creates files? 
        # No, my MockRunner in runners.py just prints.
        # The generators have logic: "if isinstance(self.runner, MockRunner): create dummy file"
        
        # So if we make DockerRunner look like MockRunner, it might work?
        # No, isinstance checks class identity.
        
        # Strategy: Patch 'pepdesign.runners.DockerRunner' to be 'pepdesign.runners.MockRunner'
        from pepdesign.runners import MockRunner
        # MockRunner doesn't take args, but DockerRunner does.
        MockDocker.side_effect = lambda *args, **kwargs: MockRunner()
        
        # Test RFdiffusion
        print("\n[Test 1] RFdiffusion")
        config_rf = PipelineConfig(
            global_settings=GlobalConfig(output_dir=output_dir + "/rf", seed=42),
            target=TargetConfig(pdb_path=test_pdb, mode="de_novo", target_chain="A", binding_site_residues=[1]),
            backbone=BackboneConfig(generator_type="rfdiffusion", num_backbones=1, peptide_length=5),
            design=DesignConfig(designer_type="stub", num_sequences_per_backbone=1),
            scoring=ScoringConfig()
        )
        pipeline_rf = PepDesignPipeline(config_rf)
        pipeline_rf.run()
        # Implementation uses rfdiffusion_out_{i}.pdb
        assert os.path.exists(os.path.join(output_dir, "rf/backbones/rfdiffusion_out_0.pdb"))
        print("  ✓ RFdiffusion pipeline ran (Mocked)")

        # Test DiffPepBuilder
        print("\n[Test 2] DiffPepBuilder")
        config_dp = PipelineConfig(
            global_settings=GlobalConfig(output_dir=output_dir + "/dp", seed=42),
            target=TargetConfig(pdb_path=test_pdb, mode="de_novo", target_chain="A", binding_site_residues=[1]),
            backbone=BackboneConfig(generator_type="diffpepbuilder", num_backbones=1, peptide_length=5),
            design=DesignConfig(designer_type="stub", num_sequences_per_backbone=1),
            scoring=ScoringConfig()
        )
        pipeline_dp = PepDesignPipeline(config_dp)
        pipeline_dp.run()
        # Implementation uses generated_{i}.pdb
        assert os.path.exists(os.path.join(output_dir, "dp/backbones/generated_0.pdb"))
        print("  ✓ DiffPepBuilder pipeline ran (Mocked)")
    
    print("\n✅ Generator Verification Passed!")

if __name__ == "__main__":
    test_generators_integration()
