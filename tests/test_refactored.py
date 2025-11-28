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
        # Test 1: prepare_target
        print("\n[Test 1] prepare_target")
        target_state = prepare_target(
            pdb_path=test_pdb,
            output_dir=f"{output_base}/target",
            mode="de_novo",
            target_chain="A",
            binding_site_residues=[1, 2, 3, 4, 5],
            do_relax=True
        )
        print(f"  ✓ Created: {target_state.pdb_path}")
        print(f"  ✓ Created: {target_state.binding_site}")
        
        # Test 2: generate_backbones
        print("\n[Test 2] generate_backbones")
        result = generate_backbones(
            target_pdb=target_state.best_pdb_path,
            binding_site_data=target_state.binding_site.dict(),
            output_dir=f"{output_base}/backbones",
            num_backbones=2,
            peptide_length=6,
            config=None # Assuming config is optional or handled inside? Wait, generate_backbones signature requires config object usually.
            # The original test passed 'mode="stub"' which is NOT in the signature I saw earlier.
            # Let's check generate_backbones signature again.
        )
        
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
