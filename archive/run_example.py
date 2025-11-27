"""
MDM2-p53 Peptide Optimization Example

This example demonstrates the optimize_existing mode of the pipeline:
1. Prepare target: Extract MDM2 target and p53 peptide from complex
2. Generate backbones: Create backbone_0 from existing + perturbed variants
3. Design sequences: Redesign with constraints (fixed key positions)
4. Score sequences: Compute physicochemical properties
5. Rank sequences: Rank by composite score

The p53 peptide (ETFSDLWKLL) binds to MDM2 with key residues F3, W7, L10.
We'll fix positions 3 and 7 (F and W) and allow variation elsewhere.
"""
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath('../..'))

from pepdesign.modules import (
    prepare_target,
    generate_backbones,
    design_sequences,
    score_sequences,
    rank_sequences
)

def load_config(config_file):
    """Load JSON config file."""
    with open(config_file, 'r') as f:
        return json.load(f)

def run_mdm2_p53_example():
    """Run the complete MDM2-p53 optimization pipeline."""
    
    print("=" * 60)
    print("MDM2-p53 Peptide Optimization Example")
    print("=" * 60)
    
    # Change to example directory
    example_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(example_dir)
    
    # Step 1: Prepare Target
    print("\n[Step 1/5] Preparing target structure...")
    config = load_config("config_prepare.json")
    result = prepare_target(**config)
    print(f"  ✓ Created: {result['clean_pdb']}")
    print(f"  ✓ Created: {result['binding_site_json']}")
    print(f"  ✓ Created: {result['existing_peptide_json']}")
    
    # Step 2: Generate Backbones
    print("\n[Step 2/5] Generating backbones...")
    config = load_config("config_backbones.json")
    result = generate_backbones(**config)
    print(f"  ✓ Generated {len(result['backbone_pdbs'])} backbones")
    print(f"  ✓ Created: {result['index_csv']}")
    
    # Step 3: Design Sequences
    print("\n[Step 3/5] Designing sequences...")
    config = load_config("config_design.json")
    design_sequences(**config)
    print(f"  ✓ Created: {config['output_csv']}")
    
    # Step 4: Score Sequences
    print("\n[Step 4/5] Scoring sequences...")
    config = load_config("config_score.json")
    score_sequences(**config)
    print(f"  ✓ Created: {config['output_csv']}")
    
    # Step 5: Rank Sequences
    print("\n[Step 5/5] Ranking sequences...")
    config = load_config("config_rank.json")
    rank_sequences(**config)
    print(f"  ✓ Created: {config['output_csv']}")
    
    # Display top results
    print("\n" + "=" * 60)
    print("Top 5 Designed Sequences:")
    print("=" * 60)
    
    import pandas as pd
    df = pd.read_csv(config['output_csv'])
    
    for i, row in df.head(5).iterrows():
        print(f"\nRank {row['rank']}: {row['design_id']}")
        print(f"  Sequence: {row['peptide_seq']}")
        print(f"  Composite Score: {row['composite_score']:.3f}")
        print(f"  Net Charge: {row['net_charge']:.2f}")
        print(f"  Hydrophobic Fraction: {row['hydrophobic_fraction']:.2f}")
        print(f"  Passes Filters: {row['passes_filters']}")
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)
    print(f"\nResults saved in: {os.path.join(example_dir, 'output')}")

if __name__ == "__main__":
    run_mdm2_p53_example()
