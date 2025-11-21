from pepdesign.modules.prepare_target import prepare_target
import os
import json

def test_prepare_target():
    print("Testing prepare_target module...")
    
    output_dir = "test_output"
    pdb_path = "dummy_test.pdb"
    
    # Test 1: Optimize Existing Mode
    print("\n[Test 1] Optimize Existing Mode")
    try:
        prepare_target(
            pdb_path=pdb_path,
            output_dir=output_dir,
            mode="optimize_existing",
            target_chain="A",
            peptide_chain="B"
        )
        print("Success!")
        
        # Check files
        if os.path.exists(os.path.join(output_dir, "target_clean.pdb")):
            print(" - target_clean.pdb created")
        if os.path.exists(os.path.join(output_dir, "binding_site.json")):
            with open(os.path.join(output_dir, "binding_site.json")) as f:
                data = json.load(f)
                print(f" - binding_site.json: {data}")
        if os.path.exists(os.path.join(output_dir, "existing_peptide.json")):
            with open(os.path.join(output_dir, "existing_peptide.json")) as f:
                data = json.load(f)
                print(f" - existing_peptide.json: {data}")
                
    except Exception as e:
        print(f"Failed: {e}")

    # Test 2: De Novo Manual Mode
    print("\n[Test 2] De Novo Manual Mode")
    try:
        prepare_target(
            pdb_path=pdb_path,
            output_dir=output_dir,
            mode="de_novo",
            target_chain="A",
            binding_site_residues=[1, 2]
        )
        print("Success!")
        
        if os.path.exists(os.path.join(output_dir, "binding_site.json")):
            with open(os.path.join(output_dir, "binding_site.json")) as f:
                data = json.load(f)
                print(f" - binding_site.json: {data}")
                
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_prepare_target()
