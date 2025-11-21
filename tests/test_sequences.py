from pepdesign.modules.design_sequences import design_sequences
import os
import pandas as pd

def test_sequence_design():
    print("Testing sequence design module...")
    
    backbones_dir = "test_backbones"
    output_csv = "test_sequences.csv"
    
    # Ensure inputs exist (from previous test)
    if not os.path.exists(os.path.join(backbones_dir, "index.csv")):
        print("Skipping test: test_backbones/index.csv not found. Run test_backbone.py first.")
        return

    # Test 1: De Novo Mode
    print("\n[Test 1] De Novo Mode")
    try:
        design_sequences(
            backbones_dir=backbones_dir,
            output_csv=output_csv,
            mode="de_novo",
            target_chain="A",
            peptide_chain="B",
            num_sequences_per_backbone=3
        )
        print("Success!")
        
        # Check output
        if os.path.exists(output_csv):
            df = pd.read_csv(output_csv)
            print(f" - Created {len(df)} designs")
            print(f" - Sample design:\n{df.head(1)}")
            
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Optimize Existing Mode with Fixed Positions
    print("\n[Test 2] Optimize Existing Mode with Fixed Positions")
    try:
        fixed_positions = {
            "backbone_0": [1, 2, 3],  # Fix first 3 positions
            "backbone_1": [5, 6]       # Fix positions 5 and 6
        }
        
        design_sequences(
            backbones_dir=backbones_dir,
            output_csv="test_sequences_opt.csv",
            mode="optimize_existing",
            target_chain="A",
            peptide_chain="B",
            num_sequences_per_backbone=2,
            fixed_positions=fixed_positions
        )
        print("Success!")
        
        if os.path.exists("test_sequences_opt.csv"):
            df = pd.read_csv("test_sequences_opt.csv")
            print(f" - Created {len(df)} designs")
            print(f" - Sample sequence with fixed positions: {df.iloc[0]['peptide_seq']}")
            
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sequence_design()
