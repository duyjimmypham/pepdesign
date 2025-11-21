from pepdesign.modules.score_sequences import score_sequences
from pepdesign.utils import (
    compute_net_charge,
    estimate_pI,
    hydrophobic_fraction,
    count_cysteines,
    has_aggregation_motif
)
import os
import pandas as pd

def test_scoring_functions():
    print("Testing scoring helper functions...")
    
    # Test sequences
    test_seqs = {
        "ACDEFGHIKL": "Mixed",
        "KKKRRR": "Highly positive",
        "DDDEEEE": "Highly negative",
        "AVILMFWY": "Hydrophobic",
        "CCCCCC": "Many cysteines",
        "WWWAAAA": "Aggregation prone"
    }
    
    print("\n[Test 1] Helper Functions")
    for seq, desc in test_seqs.items():
        charge = compute_net_charge(seq, ph=7.4)
        pi = estimate_pI(seq)
        hydro = hydrophobic_fraction(seq)
        cys = count_cysteines(seq)
        agg = has_aggregation_motif(seq)
        
        print(f"\n{desc}: {seq}")
        print(f"  Net charge (pH 7.4): {charge:.2f}")
        print(f"  pI: {pi:.2f}")
        print(f"  Hydrophobic fraction: {hydro:.2f}")
        print(f"  Cys count: {cys}")
        print(f"  Aggregation flag: {agg}")

def test_score_sequences_module():
    print("\n\n[Test 2] score_sequences() function")
    
    sequences_csv = "test_sequences.csv"
    output_csv = "test_scores.csv"
    
    # Ensure input exists
    if not os.path.exists(sequences_csv):
        print(f"Skipping test: {sequences_csv} not found. Run test_sequences.py first.")
        return
    
    try:
        score_sequences(
            sequences_csv=sequences_csv,
            output_csv=output_csv,
            ph=7.4,
            charge_min=-5.0,
            charge_max=8.0,
            max_hydrophobic_fraction=0.6,
            max_cys_count=2
        )
        print("Success!")
        
        # Check output
        if os.path.exists(output_csv):
            df = pd.read_csv(output_csv)
            print(f"\n - Scored {len(df)} sequences")
            print(f" - Columns: {list(df.columns)}")
            print(f"\n - Sample scored sequence:")
            print(df[['design_id', 'peptide_seq', 'net_charge', 'pI', 'hydrophobic_fraction', 'filtered_out']].head(3))
            
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scoring_functions()
    test_score_sequences_module()
