"""
Abstract Base Classes (interfaces) for PepDesign components.
Defines the contracts that all implementations must follow.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from pepdesign.config import BackboneConfig, DesignConfig

@dataclass
class BackboneResult:
    """Standardized result from backbone generation."""
    backbone_id: str
    pdb_path: str
    peptide_chain_id: str
    metadata: Dict[str, Any]

@dataclass
class DesignResult:
    """Standardized result from sequence design."""
    design_id: str
    backbone_id: str
    sequence: str
    score: float
    metadata: Dict[str, Any]

class BackboneGenerator(ABC):
    """Interface for backbone generation tools (e.g., RFdiffusion, Stub)."""
    
    @abstractmethod
    def generate(
        self,
        target_pdb: str,
        binding_site_data: Dict[str, Any],
        output_dir: str,
        config: BackboneConfig,
        existing_peptide_data: Dict[str, Any] = None
    ) -> List[BackboneResult]:
        """
        Generate peptide backbones.
        
        Args:
            target_pdb: Path to cleaned target PDB
            binding_site_data: Dictionary containing binding site center, radius, etc.
            output_dir: Directory to save generated PDBs
            config: Backbone generation configuration
            existing_peptide_data: Optional data for 'optimize_existing' mode
            
        Returns:
            List of BackboneResult objects
        """
        pass

class SequenceDesigner(ABC):
    """Interface for sequence design tools (e.g., ProteinMPNN, Stub)."""
    
    @abstractmethod
    def design(
        self,
        backbone_results: List[BackboneResult],
        output_dir: str,
        config: DesignConfig,
        global_constraints: Dict[str, Any] = None
    ) -> List[DesignResult]:
        """
        Design sequences for the given backbones.
        
        Args:
            backbone_results: List of backbones to design on
            output_dir: Directory to save design artifacts
            config: Sequence design configuration
            global_constraints: Optional global constraints
            
        Returns:
            List of DesignResult objects
        """
        pass
