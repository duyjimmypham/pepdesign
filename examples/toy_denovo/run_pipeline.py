"""
PepDesign Pipeline - Toy De Novo Example

This example demonstrates de novo peptide design for a synthetic binding pocket.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from pepdesign.pipeline import PepDesignPipeline
from pepdesign.config import GlobalConfig, TargetConfig, BackboneConfig, DesignConfig, ScoringConfig

def main():
    # Initialize pipeline
    pipeline = PepDesignPipeline(
        output_dir="output",
        config=GlobalConfig(random_seed=42)
    )
    
    # Step 1: Prepare target
    print("\n=== Step 1: Target Preparation ===")
    pipeline.prepare_target(
        pdb_path="toy_target.pdb",
        config=TargetConfig(
            mode="de_novo",
            target_chain="A",
            binding_site_residues=[10, 11, 12, 45, 46, 47]  # Example pocket residues
        )
    )
    
    # Step 2: Generate backbones
    print("\n=== Step 2: Backbone Generation ===")
    pipeline.generate_backbones(
        config=BackboneConfig(
            generator_type="stub",
            num_backbones=3,
            peptide_length=8
        )
    )
    
    # Step 3: Design sequences
    print("\n=== Step 3: Sequence Design ===")
    pipeline.design_sequences(
        config=DesignConfig(
            designer_type="stub",
            num_sequences=10
        )
    )
    
    # Step 4: Score and rank
    print("\n=== Step 4: Scoring and Ranking ===")
    pipeline.score_and_rank(
        config=ScoringConfig(
            ph=7.4,
            charge_min=-2.0,
            charge_max=2.0,
            max_hydrophobic_fraction=0.6,
            max_cys_count=2
        )
    )
    
    print("\n=== Pipeline Complete ===")
    print(f"Results saved to: {pipeline.ctx.output_dir}")
    print(f"View report: {pipeline.ctx.output_dir}/report.html")

if __name__ == "__main__":
    main()
