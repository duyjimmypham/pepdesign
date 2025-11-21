"""
Chemistry utility functions for peptide sequence analysis.
Centralizes all physicochemical property calculations.
"""
import math
from typing import Dict

# pKa values for ionizable groups
PKA_VALUES = {
    'N_term': 9.0,
    'C_term': 2.0,
    'D': 3.9,  # Asp
    'E': 4.3,  # Glu
    'K': 10.5, # Lys
    'R': 12.5, # Arg
    'H': 6.0,  # His
    'C': 8.3,  # Cys
    'Y': 10.1, # Tyr
}

HYDROPHOBIC_RESIDUES = set('AVILMFWY')

def compute_net_charge(sequence: str, ph: float = 7.4) -> float:
    """
    Compute net charge using Henderson-Hasselbalch equation.
    
    Args:
        sequence: Amino acid sequence
        ph: pH value
        
    Returns:
        Net charge at given pH
    """
    if not sequence:
        return 0.0
    
    charge = 0.0
    
    # N-terminus (positive when protonated)
    charge += 1.0 / (1.0 + 10**(ph - PKA_VALUES['N_term']))
    
    # C-terminus (negative when deprotonated)
    charge -= 1.0 / (1.0 + 10**(PKA_VALUES['C_term'] - ph))
    
    # Side chains
    for aa in sequence:
        if aa in ('D', 'E'):
            # Acidic - negative when deprotonated
            pka = PKA_VALUES.get(aa, 4.0)
            charge -= 1.0 / (1.0 + 10**(pka - ph))
        elif aa in ('K', 'R'):
            # Basic - positive when protonated
            pka = PKA_VALUES.get(aa, 10.0)
            charge += 1.0 / (1.0 + 10**(ph - pka))
        elif aa == 'H':
            # Histidine - weakly basic
            charge += 1.0 / (1.0 + 10**(ph - PKA_VALUES['H']))
    
    return charge

def estimate_pI(sequence: str) -> float:
    """
    Estimate isoelectric point using binary search.
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        Estimated pI
    """
    if not sequence:
        return 7.0
    
    # Binary search for pH where charge is closest to 0
    ph_low = 0.0
    ph_high = 14.0
    
    for _ in range(20):  # 20 iterations for convergence
        ph_mid = (ph_low + ph_high) / 2.0
        charge = compute_net_charge(sequence, ph_mid)
        
        if abs(charge) < 0.01:
            return ph_mid
        
        if charge > 0:
            ph_low = ph_mid
        else:
            ph_high = ph_mid
    
    return (ph_low + ph_high) / 2.0

def hydrophobic_fraction(sequence: str) -> float:
    """
    Calculate fraction of hydrophobic residues (AVILMFWY).
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        Fraction of hydrophobic residues
    """
    if not sequence:
        return 0.0
    
    hydrophobic_count = sum(1 for aa in sequence if aa in HYDROPHOBIC_RESIDUES)
    return hydrophobic_count / len(sequence)

def count_cysteines(sequence: str) -> int:
    """
    Count number of cysteine residues.
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        Number of cysteines
    """
    return sequence.count('C')

def has_aggregation_motif(sequence: str) -> bool:
    """
    Detect problematic aggregation motifs.
    
    Checks for:
    - Long hydrophobic runs (>= 4 consecutive)
    - Specific patterns (WWW, FFF, III)
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        True if aggregation-prone motifs detected
    """
    # Check for long hydrophobic runs
    hydrophobic_run = 0
    for aa in sequence:
        if aa in HYDROPHOBIC_RESIDUES:
            hydrophobic_run += 1
            if hydrophobic_run >= 4:
                return True
        else:
            hydrophobic_run = 0
    
    # Check for specific problematic patterns
    if 'WWW' in sequence or 'FFF' in sequence or 'III' in sequence:
        return True
    
    return False

def sequence_length(sequence: str) -> int:
    """
    Get length of sequence.
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        Length of sequence
    """
    return len(sequence)

def aromatic_fraction(sequence: str) -> float:
    """
    Calculate fraction of aromatic residues (F, W, Y).
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        Fraction of aromatic residues
    """
    if not sequence:
        return 0.0
    count = sum(1 for aa in sequence if aa in 'FWY')
    return count / len(sequence)

def positive_fraction(sequence: str) -> float:
    """
    Calculate fraction of basic/positive residues (K, R, H).
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        Fraction of positive residues
    """
    if not sequence:
        return 0.0
    count = sum(1 for aa in sequence if aa in 'KRH')
    return count / len(sequence)

def negative_fraction(sequence: str) -> float:
    """
    Calculate fraction of acidic/negative residues (D, E).
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        Fraction of negative residues
    """
    if not sequence:
        return 0.0
    count = sum(1 for aa in sequence if aa in 'DE')
    return count / len(sequence)

def polar_fraction(sequence: str) -> float:
    """
    Calculate fraction of polar uncharged residues (S, T, N, Q).
    
    Args:
        sequence: Amino acid sequence
        
    Returns:
        Fraction of polar residues
    """
    if not sequence:
        return 0.0
    count = sum(1 for aa in sequence if aa in 'STNQ')
    return count / len(sequence)
