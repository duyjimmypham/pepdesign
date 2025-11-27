"""
Pipeline orchestrator.
Manages the end-to-end execution of the PepDesign workflow.
"""
import os
import json
import random
import numpy as np
from typing import Optional

from pepdesign.config import PipelineConfig
from pepdesign.context import ProjectContext
from pepdesign.modules.prepare_target import prepare_target
from pepdesign.modules.generate_backbones import get_backbone_generator
from pepdesign.modules.design_sequences import get_sequence_designer
from pepdesign.modules.score_sequences import score_sequences, compute_reference_properties
from pepdesign.modules.ranking import rank_sequences

class PepDesignPipeline:
    """
    Orchestrates the peptide design pipeline.
    """
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.ctx = ProjectContext(config)
        
        # Set random seeds
        self._set_seeds(config.global_settings.seed)
        
        # Initialize components
        self.backbone_generator = get_backbone_generator(config.backbone)
        self.sequence_designer = get_sequence_designer(config.design)
        
    def _set_seeds(self, seed: int):
        random.seed(seed)
        np.random.seed(seed)
        # torch.manual_seed(seed) # If using torch
        
    def run(self):
        """Execute the full pipeline."""
        print(f"Starting PepDesign Pipeline (Seed: {self.config.global_settings.seed})")
        print(f"Output Directory: {self.ctx.root_dir}")
        
        # 1. Prepare Target
        print("\n[Step 1] Preparing Target...")
        prep_result = prepare_target(
            pdb_path=self.config.target.pdb_path,
            output_dir=self.ctx.dirs["target"],
            mode=self.config.target.mode,
            target_chain=self.config.target.target_chain,
            binding_site_residues=self.config.target.binding_site_residues,
            peptide_chain=self.config.target.peptide_chain,
            contact_cutoff=self.config.target.contact_cutoff,
            keep_cofactors=self.config.target.keep_cofactors
        )
        
        # Load binding site data
        with open(self.ctx.binding_site_json, 'r') as f:
            binding_site_data = json.load(f)
            
        existing_peptide_data = None
        if self.config.target.mode == "optimize_existing":
            with open(self.ctx.existing_peptide_json, 'r') as f:
                existing_peptide_data = json.load(f)
                
            # Compute reference properties
            compute_reference_properties(
                existing_peptide_json=self.ctx.existing_peptide_json,
                output_json=self.ctx.reference_properties_json,
                ph=self.config.scoring.ph
            )

        # 2. Generate Backbones
        print("\n[Step 2] Generating Backbones...")
        backbone_results = self.backbone_generator.generate(
            target_pdb=self.ctx.clean_target_pdb,
            binding_site_data=binding_site_data,
            output_dir=self.ctx.dirs["backbones"],
            config=self.config.backbone,
            existing_peptide_data=existing_peptide_data
        )
        
        # 3. Design Sequences
        print("\n[Step 3] Designing Sequences...")
        
        # Construct constraints dictionary from config
        global_constraints = {}
        if self.config.design.fixed_positions_global:
            global_constraints["fixed_positions_global"] = self.config.design.fixed_positions_global
        if self.config.design.fixed_residues_global:
            global_constraints["fixed_residues_global"] = self.config.design.fixed_residues_global
            
        design_results = self.sequence_designer.design(
            backbone_results=backbone_results,
            output_dir=self.ctx.dirs["designs"],
            config=self.config.design,
            global_constraints=global_constraints
        )
        
        # 4. Score Sequences
        print("\n[Step 4] Scoring Sequences...")
        score_sequences(
            sequences_csv=self.ctx.sequences_csv,
            output_csv=self.ctx.scored_csv,
            ph=self.config.scoring.ph,
            charge_min=self.config.scoring.charge_min,
            charge_max=self.config.scoring.charge_max,
            max_hydrophobic_fraction=self.config.scoring.max_hydrophobic_fraction,
            max_cys_count=self.config.scoring.max_cys_count
        )
        
        # 5. Rank Sequences
        print("\n[Step 5] Ranking Sequences...")
        
        rank_sequences(
            scored_csv=self.ctx.scored_csv,
            output_csv=self.ctx.ranked_csv,
            reference_properties_json=self.ctx.reference_properties_json if self.config.target.mode == "optimize_existing" else None
        )
        
        # 6. Generate Report
        print("\n[Step 6] Generating Report...")
        from pepdesign.reporting import generate_html_report
        
        generate_html_report(
            ranked_csv=self.ctx.ranked_csv,
            output_html=os.path.join(self.ctx.root_dir, "report.html")
        )
        
        print("\nPipeline Completed Successfully!")
