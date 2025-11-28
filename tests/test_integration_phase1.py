"""
Integration test for PepDesignPipeline (Phase 1).
"""
import os
import shutil
from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import PipelineConfig, GlobalConfig, TargetConfig, BackboneConfig, DesignConfig, ScoringConfig

def test_pipeline_integration():
    print("Testing PepDesignPipeline Integration...")
    
    # Setup
    output_dir = "test_pipeline_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    test_pdb = "tests/dummy_test.pdb"
    # Ensure dummy PDB exists (created by previous test, but let's be safe)
    if not os.path.exists(test_pdb):
        with open(test_pdb, "w") as f:
            f.write("ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00  0.00           N\n")
            f.write("ATOM      2  CA  ALA A   1      11.458  10.000  10.000  1.00  0.00           C\n")
            f.write("ATOM      3  C   ALA A   1      12.000  11.400  10.000  1.00  0.00           C\n")
            f.write("ATOM      4  O   ALA A   1      11.500  12.300  10.000  1.00  0.00           O\n")
            f.write("ATOM      5  CB  ALA A   1      12.000   9.000  10.000  1.00  0.00           C\n")

    # Config
    config = PipelineConfig(
        global_settings=GlobalConfig(output_dir=output_dir, seed=42),
        target=TargetConfig(
            pdb_path=test_pdb,
            mode="de_novo",
            target_chain="A",
            binding_site_residues=[1]
        ),
        backbone=BackboneConfig(
            generator_type="stub",
            num_backbones=2,
            peptide_length=5
        ),
        design=DesignConfig(
            designer_type="stub",
            num_sequences_per_backbone=2
        ),
        scoring=ScoringConfig()
    )
    
    # Initialize Pipeline
    pipeline = PepDesignPipeline(config)
    
    # Run
    try:
        pipeline.run()
        print("\n✅ Pipeline ran successfully!")
        
        # Verify outputs
        target_dir = os.path.join(output_dir, "target")
        assert os.path.exists(os.path.join(target_dir, "target_clean.pdb"))
        assert os.path.exists(os.path.join(target_dir, "binding_site.json"))
        # Check for relaxed PDB (might fail if PyRosetta missing, but MockRelaxer should handle it)
        # Wait, get_relaxer defaults to MockRelaxer if PyRosetta missing? Yes.
        # But prepare_target catches exception.
        
        backbones_dir = os.path.join(output_dir, "backbones")
        assert os.path.exists(os.path.join(backbones_dir, "backbone_0.pdb"))
        
        print("  ✓ Output files verified")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_pipeline_integration()
