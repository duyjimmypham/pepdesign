"""
Integration test for ProteinMPNN (Phase 1).
"""
import os
import shutil
from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import PipelineConfig, GlobalConfig, TargetConfig, BackboneConfig, DesignConfig, ScoringConfig

def test_protein_mpnn_integration():
    print("Testing ProteinMPNN Integration...")
    
    output_dir = "test_mpnn_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    test_pdb = "tests/dummy_test.pdb"
    if not os.path.exists(test_pdb):
        with open(test_pdb, "w") as f:
            f.write("ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00  0.00           N\n")

    # Mock DockerRunner
    from unittest.mock import patch, MagicMock
    from pepdesign.runners import MockRunner
    
    with patch('pepdesign.runners.DockerRunner') as MockDocker:
        MockDocker.side_effect = lambda *args, **kwargs: MockRunner()
        
        # Test ProteinMPNN
        print("\n[Test 1] ProteinMPNN")
        config = PipelineConfig(
            global_settings=GlobalConfig(output_dir=output_dir, seed=42),
            target=TargetConfig(pdb_path=test_pdb, mode="de_novo", target_chain="A", binding_site_residues=[1]),
            backbone=BackboneConfig(generator_type="stub", num_backbones=1, peptide_length=5),
            design=DesignConfig(designer_type="protein_mpnn", num_sequences_per_backbone=2),
            scoring=ScoringConfig()
        )
        pipeline = PepDesignPipeline(config)
        pipeline.run()
        
        # Verify output
        # Should have generated sequences.csv
        assert os.path.exists(os.path.join(output_dir, "designs/sequences.csv"))
        
        # Should have generated FASTA files in seqs/
        # Note: StubBackboneGenerator creates 'backbone_0.pdb'
        assert os.path.exists(os.path.join(output_dir, "designs/seqs/backbone_0.fa"))
        
        print("  ✓ ProteinMPNN pipeline ran (Mocked)")
    
    print("\n✅ ProteinMPNN Verification Passed!")

if __name__ == "__main__":
    test_protein_mpnn_integration()
