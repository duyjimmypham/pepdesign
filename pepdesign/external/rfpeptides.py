"""
Stub wrapper for RFpeptides/RFdiffusion backbone generation.
"""
from typing import List, Dict, Optional

def run_rfpeptides(
    target_pdb: str,
    binding_site_json: str,
    output_pdb: str,
    peptide_length: int,
    config: Optional[Dict] = None,
) -> None:
    """
    Thin wrapper for RFpeptides / RFdiffusion macrocycle binder protocol.
    
    Args:
        target_pdb: Path to target PDB
        binding_site_json: Path to binding site metadata
        output_pdb: Path for output backbone PDB
        peptide_length: Length of peptide to generate
        config: Optional config dict (paths, flags, etc.)
        
    TODO: Integrate real RFpeptides/RFdiffusion:
    - Read config for paths and flags (rf_diffusion_exe, protocol script)
    - Build RFpeptides command with appropriate flags
    - Run via subprocess
    - Handle macrocycle constraints
    - Parse output and validate
    """
    raise NotImplementedError("RFpeptides backend is not implemented yet.")
