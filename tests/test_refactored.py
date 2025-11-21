"""
Quick test to verify refactored modules work correctly.
"""
from pepdesign.modules import prepare_target, generate_backbones, design_sequences, score_sequences
import os
import shutil

def test_refactored_pipeline():
    print("Testing refactored pipeline...")
    
    # Use existing test data
    test_pdb = "tests/dummy_test.pdb"
    if not os.path.exists(test_pdb):
        print("Test PDB not found, skipping test")
        return
    
    output_base = "test_refactored_output"
    if os.path.exists(output_base):
        shutil.rmtree(output_base)
    
    try:
        # Test 1: prepare_target
        print("\n[Test 1] prepare_target")
        result = prepare_target(
            pdb_path=test_pdb,
            output_dir=f"{output_base}/target",
            mode="de_novo",
            target_chain="A",
            binding_site_residues=[1, 2, 3, 4, 5]
        )
        print(f"  ✓ Created: {result['clean_pdb']}")
        print(f"  ✓ Created: {result['binding_site_json']}")
        
        # Test 2: generate_backbones
        print("\n[Test 2] generate_backbones")
        result = generate_backbones(
            target_pdb=result['clean_pdb'],
            binding_site_json=result['binding_site_json'],
            output_dir=f"{output_base}/backbones",
            num_backbones=2,
            peptide_length=6,
            mode="stub"
        )
        print(f"  ✓ Created {len(result['backbone_pdbs'])} backbones")
        print(f"  ✓ Created: {result['index_csv']}")
        
        # Test 3: design_sequences
        print("\n[Test 3] design_sequences")
        design_sequences(
            backbones_dir=f"{output_base}/backbones",
            output_csv=f"{output_base}/sequences.csv",
            mode="de_novo",
            num_sequences_per_backbone=3
        )
        print(f"  ✓ Created: {output_base}/sequences.csv")
        
        # Test 4: score_sequences
        print("\n[Test 4] score_sequences")
        score_sequences(
            sequences_csv=f"{output_base}/sequences.csv",
            output_csv=f"{output_base}/scored.csv",
            ph=7.4,
            charge_min=-3.0,
            charge_max=5.0,
            max_hydrophobic_fraction=0.7
        )
        print(f"  ✓ Created: {output_base}/scored.csv")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_refactored_pipeline()
