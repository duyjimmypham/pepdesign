"""
Configuration models for PepDesign pipeline.
Enforces type safety and validation for all pipeline parameters.
"""
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field, validator
import os

class GlobalConfig(BaseModel):
    """Global configuration settings."""
    seed: int = Field(42, description="Random seed for reproducibility")
    output_dir: str = Field(..., description="Root output directory")
    
    @validator('output_dir')
    def create_output_dir(cls, v):
        os.makedirs(v, exist_ok=True)
        return v

class TargetConfig(BaseModel):
    """Configuration for target preparation."""
    pdb_path: str = Field(..., description="Path to input PDB file")
    mode: Literal["de_novo", "optimize_existing"] = Field(..., description="Design mode")
    target_chain: str = Field(..., description="Chain ID of the target protein")
    peptide_chain: Optional[str] = Field(None, description="Chain ID of the existing peptide (required for optimize_existing)")
    binding_site_residues: Optional[List[int]] = Field(None, description="Manual binding site residues (for de_novo)")
    contact_cutoff: float = Field(5.0, description="Distance cutoff for binding site detection (Angstroms)")
    keep_cofactors: Optional[List[str]] = Field(None, description="List of cofactor residue names to keep")

    @validator('pdb_path')
    def pdb_must_exist(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"PDB file not found: {v}")
        return v
    
    @validator('peptide_chain')
    def validate_peptide_chain(cls, v, values):
        if values.get('mode') == 'optimize_existing' and not v:
            raise ValueError("peptide_chain is required for optimize_existing mode")
        return v

class BackboneConfig(BaseModel):
    """Configuration for backbone generation."""
    generator_type: Literal["stub", "rfdiffusion", "diffpepbuilder"] = Field("stub", description="Backbone generation backend")
    num_backbones: int = Field(10, ge=1, description="Number of backbones to generate")
    peptide_length: Optional[int] = Field(None, ge=3, description="Length of peptide (required for de_novo)")
    
    # Perturbation parameters (for optimize_existing / stub)
    translation_std: float = Field(0.5, description="Translation standard deviation (Angstroms)")
    rotation_deg: float = Field(5.0, description="Rotation standard deviation (degrees)")

class DesignConfig(BaseModel):
    """Configuration for sequence design."""
    designer_type: Literal["stub", "protein_mpnn"] = Field("stub", description="Sequence design backend")
    num_sequences_per_backbone: int = Field(5, ge=1, description="Number of sequences to sample per backbone")
    
    # Constraints
    fixed_positions_global: Optional[List[int]] = None
    fixed_residues_global: Optional[List[str]] = None
    disallowed_residues_global: Optional[List[str]] = None

class ScoringConfig(BaseModel):
    """Configuration for sequence scoring and filtering."""
    ph: float = Field(7.4, description="pH for charge calculations")
    charge_min: Optional[float] = Field(None, description="Minimum net charge")
    charge_max: Optional[float] = Field(None, description="Maximum net charge")
    max_hydrophobic_fraction: Optional[float] = Field(None, description="Maximum hydrophobic fraction")
    max_cys_count: Optional[int] = Field(None, description="Maximum cysteine count")

class PredictionConfig(BaseModel):
    """Configuration for structure prediction."""
    predictor_type: Literal["none", "alphafold2", "alphafold3", "chai1"] = Field("none", description="Structure prediction backend")
    num_models: int = Field(1, ge=1, le=5, description="Number of models to predict per sequence")
    use_templates: bool = Field(False, description="Use template-based modeling (AlphaFold2 only)")
    top_n: int = Field(5, ge=1, description="Predict structures for top N sequences only")
    model_dir: Optional[str] = Field(None, description="Path to model parameters (required for AlphaFold3)")
    
class PipelineConfig(BaseModel):
    """Master configuration for the entire pipeline."""
    global_settings: GlobalConfig
    target: TargetConfig
    backbone: BackboneConfig
    design: DesignConfig
    scoring: ScoringConfig
    prediction: PredictionConfig = Field(default_factory=PredictionConfig)
