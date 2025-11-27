"""
Verification script for PepDesign Pipeline V2.
"""
import os
import sys
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath('../..'))

from pepdesign.config import (
    PipelineConfig, GlobalConfig, TargetConfig, 
    BackboneConfig, DesignConfig, ScoringConfig
)
from pepdesign.pipeline import PepDesignPipeline

def run_verification():
    print("Running Pipeline V2 Verification...")
    
    # Define output directory
    output_dir = "output_v2"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    # Create configuration
    config = PipelineConfig(
        global_settings=GlobalConfig(
            seed=123,
            output_dir=output_dir
        ),
        target=TargetConfig(
            pdb_path="1ycr.pdb", # Assumes target.pdb exists in current dir
            mode="optimize_existing",
            target_chain="A",
            peptide_chain="B",
            contact_cutoff=5.0
        ),
        backbone=BackboneConfig(
            generator_type="stub",
            num_backbones=3,
            translation_std=0.5,
            rotation_deg=5.0
        ),
        design=DesignConfig(
            designer_type="protein_mpnn",
            num_sequences_per_backbone=2
        ),
        scoring=ScoringConfig(
            ph=7.4,
            charge_min=-5.0,
            charge_max=5.0
        )
    )
    
    # Initialize and run pipeline
    pipeline = PepDesignPipeline(config)
    pipeline.run()
    
    # Verify outputs
    expected_files = [
        os.path.join(output_dir, "target", "target_clean.pdb"),
        os.path.join(output_dir, "backbones", "index.csv"),
        os.path.join(output_dir, "designs", "sequences.csv"),
        os.path.join(output_dir, "scoring", "scored.csv"),
        os.path.join(output_dir, "ranking", "ranked.csv")
    ]
    
    print("\nVerifying output files...")
    all_exist = True
    for f in expected_files:
        if os.path.exists(f):
            print(f"  [OK] {f}")
        else:
            print(f"  [MISSING] {f}")
            all_exist = False
            
    if all_exist:
        print("\nVerification PASSED!")
    else:
        print("\nVerification FAILED!")

if __name__ == "__main__":
    run_verification()
