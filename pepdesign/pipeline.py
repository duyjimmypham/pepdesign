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
        np.random.seed(seed)
        
    def run(self):
        """Execute the full pipeline."""
        print(f"Starting PepDesign Pipeline (Seed: {self.config.global_settings.seed})")
        print(f"Output Directory: {self.ctx.root_dir}")
        
        # 1. Prepare Target
        print("\n[Step 1] Preparing Target...")
        target_state = prepare_target(
            pdb_path=self.config.target.pdb_path,
            output_dir=self.ctx.dirs["target"],
            mode=self.config.target.mode,
            target_chain=self.config.target.target_chain,
            binding_site_residues=self.config.target.binding_site_residues,
            peptide_chain=self.config.target.peptide_chain,
            contact_cutoff=self.config.target.contact_cutoff,
            keep_cofactors=self.config.target.keep_cofactors,
            do_relax=True
        )
        
        # Handle reference properties if optimizing
        if target_state.peptide_info:
            compute_reference_properties(
                existing_peptide_source=target_state.peptide_info,
                output_json=self.ctx.reference_properties_json,
                ph=self.config.scoring.ph
            )

        # 2. Generate Backbones
        print("\n[Step 2] Generating Backbones...")
        
        # Convert BindingSiteModel to dict for compatibility
        bs_data = target_state.binding_site.dict()
        
        backbone_results = self.backbone_generator.generate(
            target_pdb=target_state.best_pdb_path,
            binding_site_data=bs_data,
            output_dir=self.ctx.dirs["backbones"],
            config=self.config.backbone,
            existing_peptide_data=target_state.peptide_info.dict() if target_state.peptide_info else None
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
        
        # 6. Predict Structures (Optional)
        if self.config.prediction.predictor_type != "none":
            from pepdesign.modules.predict_structures import predict_structures
            
            predict_structures(
                ranked_csv=self.ctx.ranked_csv,
                output_dir=self.ctx.dirs["predictions"],
                config=self.config.prediction,
                target_pdb=target_state.best_pdb_path
            )
        
        # 7. Generate Report
        print("\n[Step 7] Generating Report...")
        from pepdesign.reporting import generate_html_report
        
        generate_html_report(
            ranked_csv=self.ctx.ranked_csv,
            output_html=os.path.join(self.ctx.root_dir, "report.html")
        )
        
        print("\nPipeline Completed Successfully!")
