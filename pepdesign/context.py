"""
Context management for PepDesign pipeline.
Centralizes file path handling and artifact tracking.
"""
import os
from typing import Optional
from pepdesign.config import PipelineConfig

class ProjectContext:
    """
    Manages the directory structure and file paths for a pipeline run.
    """
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.root_dir = config.global_settings.output_dir
        
        # Define standard subdirectories
        self.dirs = {
            "target": os.path.join(self.root_dir, "target"),
            "backbones": os.path.join(self.root_dir, "backbones"),
            "designs": os.path.join(self.root_dir, "designs"),
            "scoring": os.path.join(self.root_dir, "scoring"),
            "ranking": os.path.join(self.root_dir, "ranking"),
            "predictions": os.path.join(self.root_dir, "predictions"),
            "logs": os.path.join(self.root_dir, "logs"),
        }
        
        # Create directories
        for path in self.dirs.values():
            os.makedirs(path, exist_ok=True)
            
    def get_dir(self, key: str) -> str:
        """Get path to a standard subdirectory."""
        return self.dirs.get(key, self.root_dir)
    
    # Target paths
    @property
    def clean_target_pdb(self) -> str:
        return os.path.join(self.dirs["target"], "target_clean.pdb")
    
    @property
    def binding_site_json(self) -> str:
        return os.path.join(self.dirs["target"], "binding_site.json")
    
    @property
    def existing_peptide_json(self) -> str:
        return os.path.join(self.dirs["target"], "existing_peptide.json")
    
    @property
    def reference_properties_json(self) -> str:
        return os.path.join(self.dirs["target"], "reference_properties.json")
        
    # Backbone paths
    @property
    def backbone_index_csv(self) -> str:
        return os.path.join(self.dirs["backbones"], "index.csv")
        
    # Design paths
    @property
    def sequences_csv(self) -> str:
        return os.path.join(self.dirs["designs"], "sequences.csv")
        
    # Scoring paths
    @property
    def scored_csv(self) -> str:
        return os.path.join(self.dirs["scoring"], "scored.csv")
        
    # Ranking paths
    @property
    def ranked_csv(self) -> str:
        return os.path.join(self.dirs["ranking"], "ranked.csv")
