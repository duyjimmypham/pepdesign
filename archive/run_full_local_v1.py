"""
MDM2-p53 Full Local Pipeline Runner

This script runs the complete peptide optimization pipeline using
lightweight CPU-only stub backends. No GPU required.

Pipeline steps:
1. Prepare target: Extract MDM2 target and p53 peptide from complex
2. Generate backbones: Create backbone_0 from existing + perturbed variants
3. Design sequences: Redesign with constraints (stub backend)
4. Score sequences: Compute physicochemical properties
5. Rank sequences: Rank by composite score
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
    rank_sequences,
    compute_reference_properties
)

def load_config(config_file):
    """Load JSON config file."""
    with open(config_file, 'r') as f:
        return json.load(f)

def run_full_local_pipeline():
    """Run the complete MDM2-p53 optimization pipeline with stub backends."""
    
    print("=" * 70)
    print("MDM2-p53 Full Local Pipeline (Stub Mode)")
    print("=" * 70)
    print("\nThis pipeline uses lightweight CPU-only stub backends.")
    print("No GPU or external tools required.\n")
    
    # Change to example directory
    example_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(example_dir)
    
    # Step 1: Prepare Target
    print("\n" + "=" * 70)
    print("[Step 1/5] Preparing target structure...")
    print("=" * 70)
    config = load_config("config_prepare.json")
    prep_result = prepare_target(**config)
    print(f"✓ Created: {prep_result['clean_pdb']}")
    print(f"✓ Created: {prep_result['binding_site_json']}")
    print(f"✓ Created: {prep_result['existing_peptide_json']}")
    
    # Step 1b: Compute Reference Properties
    print("\n" + "=" * 70)
    print("[Step 1b] Computing reference properties...")
    print("=" * 70)
    ref_json = os.path.join("output", "target", "reference_properties.json")
    compute_reference_properties(
        existing_peptide_json=prep_result['existing_peptide_json'],
        output_json=ref_json
    )
    print(f"✓ Created: {ref_json}")
    
    # Step 2: Generate Backbones
    print("\n" + "=" * 70)
    print("[Step 2/5] Generating backbones...")
    print("=" * 70)
    config = load_config("config_backbones.json")
    back_result = generate_backbones(**config)
    print(f"✓ Generated {len(back_result['backbone_pdbs'])} backbones")
    print(f"✓ Created: {back_result['index_csv']}")
    
    # Step 3: Design Sequences
    print("\n" + "=" * 70)
    print("[Step 3/5] Designing sequences (stub backend)...")
    print("=" * 70)
    config = load_config("config_design.json")
    # Ensure stub backend is used
    config["backend"] = "stub"
    design_sequences(**config)
    print(f"✓ Created: {config['output_csv']}")
    
    # Step 4: Score Sequences
    print("\n" + "=" * 70)
    print("[Step 4/5] Scoring sequences...")
    print("=" * 70)
    config = load_config("config_score.json")
    score_sequences(**config)
    print(f"✓ Created: {config['output_csv']}")
    
    # Step 5: Rank Sequences
    print("\n" + "=" * 70)
    print("[Step 5/5] Ranking sequences...")
    print("=" * 70)
    config = load_config("config_rank.json")
    rank_sequences(**config)
    print(f"✓ Created: {config['output_csv']}")
    
    # Display summary
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    
    import pandas as pd
    
    # Load results
    sequences_df = pd.read_csv("output/sequences.csv")
    scored_df = pd.read_csv("output/scored.csv")
    ranked_df = pd.read_csv("output/ranked.csv")
    
    num_sequences = len(sequences_df)
    num_passing = scored_df['passes_filters'].sum()
    num_filtered = num_sequences - num_passing
    
    print(f"\nSequences generated: {num_sequences}")
    print(f"Sequences passing filters: {num_passing}")
    print(f"Sequences filtered out: {num_filtered}")
    
    print("\n" + "-" * 70)
    print("Top 3 Ranked Sequences:")
    print("-" * 70)
    
    for i, row in ranked_df.head(3).iterrows():
        print(f"\n#{row['rank']}: {row['design_id']}")
        print(f"  Sequence:        {row['peptide_seq']}")
        print(f"  Composite Score: {row['composite_score']:.3f}")
        print(f"  Net Charge:      {row['net_charge']:.2f}")
        print(f"  Hydrophobic:     {row['hydrophobic_fraction']:.2f}")
        print(f"  Passes Filters:  {row['passes_filters']}")
    
    print("\n" + "=" * 70)
    print("Pipeline completed successfully!")
    print("=" * 70)
    print(f"\nAll results saved in: {os.path.join(example_dir, 'output')}")
    print("\nNext steps:")
    print("  - Review ranked.csv for top candidates")
    print("  - Visualize backbones in PyMOL or ChimeraX")
    print("  - For real ProteinMPNN: use local or Colab backend (future)")

if __name__ == "__main__":
    run_full_local_pipeline()
