"""
Core data models for PepDesign.
Defines the state objects that flow through the pipeline.
"""
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
import os

class BindingSiteModel(BaseModel):
    """Physical definition of the binding pocket."""
    chain_id: str
    residue_indices: List[int]
    center: Tuple[float, float, float]
    radius: float
    source: str  # e.g., "manual", "auto_stub", "from_peptide"

class PeptideInfo(BaseModel):
    """Information about the existing peptide binder (for optimization mode)."""
    chain_id: str
    sequence: str
    residue_indices: List[int]
    original_pdb_path: str

class TargetState(BaseModel):
    """
    State object representing the prepared target protein.
    Passed from Target Preparation -> Backbone Generation.
    """
    pdb_path: str = Field(..., description="Path to the original/cleaned PDB")
    relaxed_pdb_path: Optional[str] = Field(None, description="Path to the Rosetta-relaxed PDB")
    binding_site: BindingSiteModel
    sequence: Optional[str] = Field(None, description="Sequence of the target chain")
    peptide_info: Optional[PeptideInfo] = Field(None, description="Info about existing peptide if applicable")
    
    @property
    def best_pdb_path(self) -> str:
        """Returns relaxed PDB if available, else cleaned PDB."""
        return self.relaxed_pdb_path if self.relaxed_pdb_path and os.path.exists(self.relaxed_pdb_path) else self.pdb_path

class BackboneCandidate(BaseModel):
    """
    Intermediate state: A generated backbone structure without a sequence.
    """
    id: str
    pdb_path: str
    length: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DesignCandidate(BaseModel):
    """
    Final state: A fully designed sequence on a backbone.
    """
    id: str
    backbone_id: str
    sequence: str
    scores: Dict[str, float] = Field(default_factory=dict)
    pdb_path: Optional[str] = Field(None, description="Path to structure with sidechains (if modeled)")
    metadata: Dict[str, Any] = Field(default_factory=dict)
