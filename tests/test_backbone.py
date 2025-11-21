from pepdesign.modules.generate_backbones import generate_backbones
import os
import json

def test_backbone_generation():
    print("Testing backbone generation module...")
    
    output_dir = "test_backbones"
    target_pdb = "test_output/target_clean.pdb" # Assumes test_prepare.py ran successfully
    binding_site_json = "test_output/binding_site.json"
    
    # Ensure inputs exist (from previous test)
    if not os.path.exists(target_pdb) or not os.path.exists(binding_site_json):
        print("Skipping test: Input files from test_prepare.py not found.")
        return

    # Test 1: Stub Mode
    print("\n[Test 1] Stub Mode")
    try:
        generate_backbones(
            target_pdb=target_pdb,
            binding_site_json=binding_site_json,
            output_dir=output_dir,
            num_backbones=2,
            peptide_length=8,
            mode="stub"
        )
        print("Success!")
        
        # Check files
        if os.path.exists(os.path.join(output_dir, "backbone_0.pdb")):
            print(" - backbone_0.pdb created")
        if os.path.exists(os.path.join(output_dir, "index.csv")):
            print(" - index.csv created")
            
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: RFpeptides Mode (Expect Error)
    print("\n[Test 2] RFpeptides Mode (Expect NotImplementedError)")
    try:
        generate_backbones(
            target_pdb=target_pdb,
            binding_site_json=binding_site_json,
            output_dir=output_dir,
            num_backbones=1,
            peptide_length=8,
            mode="rfpeptides"
        )
        print("Failed: Should have raised NotImplementedError")
    except NotImplementedError:
        print("Success: Raised NotImplementedError as expected")
    except Exception as e:
        print(f"Failed: Raised wrong exception {e}")

if __name__ == "__main__":
    test_backbone_generation()
