"""
Stub wrapper for ProteinMPNN sequence design.
"""
import random
from typing import List, Tuple, Optional, Dict

from pepdesign.utils import load_structure, get_chain

def design_sequences_stub(
    backbone_pdb: str,
    peptide_chain: str,
    num_samples: int,
    fixed_positions: Optional[List[int]] = None,
    fixed_residues: Optional[List[str]] = None,
    disallowed_residues: Optional[Dict[int, List[str]]] = None,
    config: Optional[Dict] = None,
) -> List[Tuple[str, float]]:
    """
    Stub sequence designer for ProteinMPNN.
    
    Args:
        backbone_pdb: Path to PDB with target + peptide backbone
        peptide_chain: Chain ID of peptide to design
        num_samples: Number of sequences to sample
        fixed_positions: Optional list of 1-based residue indices to keep fixed
        fixed_residues: Optional list of residues at fixed positions (same length as fixed_positions)
        disallowed_residues: Optional dict mapping position -> list of disallowed AAs
        config: Optional backend config
        
    Returns:
        List of (sequence, log_prob) tuples
        
    TODO: Integrate real ProteinMPNN CLI or API:
    - Write JSONL file with backbone and chain specification
    - Run ProteinMPNN script via subprocess
    - Parse output sequences and scores
    - Handle fixed positions via tied_positions or fixed_positions flags
    - Handle disallowed residues via omit_AAs parameter
    """
    # Parse peptide length from PDB
    structure = load_structure(backbone_pdb)
    chain = get_chain(structure, peptide_chain)
    
    if not chain:
        raise ValueError(f"Chain {peptide_chain} not found in {backbone_pdb}")
    
    residues = list(chain)
    length = len(residues)
    
    # Validate fixed_positions and fixed_residues
    if fixed_positions and fixed_residues:
        if len(fixed_positions) != len(fixed_residues):
            raise ValueError("fixed_positions and fixed_residues must have same length")
    
    # Generate random sequences (STUB)
    results = []
    aa_alphabet = "ACDEFGHIKLMNPQRSTVWY"
    
    for _ in range(num_samples):
        seq_chars = []
        for i in range(1, length + 1):
            if fixed_positions and i in fixed_positions:
                # Use actual residue at fixed position
                idx = fixed_positions.index(i)
                if fixed_residues and idx < len(fixed_residues):
                    seq_chars.append(fixed_residues[idx])
                else:
                    # Fallback: use random (shouldn't happen if API used correctly)
                    seq_chars.append(random.choice(aa_alphabet))
            else:
                # Get allowed AAs for this position
                if disallowed_residues and i in disallowed_residues:
                    disallowed = set(disallowed_residues[i])
                    allowed = [aa for aa in aa_alphabet if aa not in disallowed]
                    if not allowed:
                        allowed = list(aa_alphabet)  # Fallback if all disallowed
                else:
                    allowed = list(aa_alphabet)
                
                seq_chars.append(random.choice(allowed))
        
        sequence = "".join(seq_chars)
        
        # Fake log prob: -length * 1.0 + noise
        log_prob = -float(length) + random.uniform(-2.0, 2.0)
        
        results.append((sequence, log_prob))
    
    return results
