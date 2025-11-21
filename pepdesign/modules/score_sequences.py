"""
Sequence scoring module.
Computes physicochemical properties and filters sequences.
"""
import pandas as pd
from typing import Optional

from pepdesign.utils import (
    load_csv,
    save_csv,
    compute_net_charge,
    estimate_pI,
    hydrophobic_fraction,
    count_cysteines,
    has_aggregation_motif,
    sequence_length,
    aromatic_fraction,
    positive_fraction,
    negative_fraction,
    polar_fraction,
    load_json,
    save_json,
)

def score_sequences(
    sequences_csv: str,
    output_csv: str,
    ph: float = 7.4,
    charge_min: Optional[float] = None,
    charge_max: Optional[float] = None,
    max_hydrophobic_fraction: Optional[float] = None,
    max_cys_count: Optional[int] = None,
) -> None:
    """
    Read designed peptide sequences, compute physicochemical scores, and filter.
    
    Args:
        sequences_csv: Input CSV with at least 'peptide_seq' column
        output_csv: Path to write scored CSV
        ph: pH for net charge calculation
        charge_min: Minimum allowed net charge (filter)
        charge_max: Maximum allowed net charge (filter)
        max_hydrophobic_fraction: Maximum allowed hydrophobic fraction (filter)
        max_cys_count: Maximum allowed number of cysteines (filter)
        
    Writes:
        CSV with added columns: net_charge, pI, hydrophobic_fraction, 
        cys_count, agg_flag, passes_filters
    """
    print(f"[ScoreSequences] Reading sequences from {sequences_csv}...")
    
    # Read input CSV
    df = load_csv(sequences_csv)
    
    # Check required columns
    if 'peptide_seq' not in df.columns:
        raise ValueError("sequences_csv must contain 'peptide_seq' column")
    
    print(f"[ScoreSequences] Computing physicochemical properties for {len(df)} sequences...")
    
    # Compute properties using centralized chemistry functions
    df['net_charge'] = df['peptide_seq'].apply(lambda seq: compute_net_charge(seq, ph))
    df['pI'] = df['peptide_seq'].apply(estimate_pI)
    df['hydrophobic_fraction'] = df['peptide_seq'].apply(hydrophobic_fraction)
    df['cys_count'] = df['peptide_seq'].apply(count_cysteines)
    df['agg_flag'] = df['peptide_seq'].apply(has_aggregation_motif)
    
    # New properties
    df['length'] = df['peptide_seq'].apply(sequence_length)
    df['aromatic_fraction'] = df['peptide_seq'].apply(aromatic_fraction)
    df['positive_fraction'] = df['peptide_seq'].apply(positive_fraction)
    df['negative_fraction'] = df['peptide_seq'].apply(negative_fraction)
    df['polar_fraction'] = df['peptide_seq'].apply(polar_fraction)
    
    # Apply filters
    df['passes_filters'] = True
    
    if charge_min is not None:
        df.loc[df['net_charge'] < charge_min, 'passes_filters'] = False
    
    if charge_max is not None:
        df.loc[df['net_charge'] > charge_max, 'passes_filters'] = False
    
    if max_hydrophobic_fraction is not None:
        df.loc[df['hydrophobic_fraction'] > max_hydrophobic_fraction, 'passes_filters'] = False
    
    if max_cys_count is not None:
        df.loc[df['cys_count'] > max_cys_count, 'passes_filters'] = False
    
    # Write output
    save_csv(df, output_csv)
    
    num_passed = df['passes_filters'].sum()
    num_filtered = len(df) - num_passed
    
    print(f"[ScoreSequences] Wrote {len(df)} scored sequences to {output_csv}")
    print(f"  - Passed filters: {num_passed}")
    print(f"  - Filtered out: {num_filtered}")

def compute_reference_properties(
    existing_peptide_json: str,
    output_json: str,
    ph: float = 7.4
) -> None:
    """
    Compute physicochemical properties for the reference peptide.
    
    Args:
        existing_peptide_json: Path to existing_peptide.json (from prepare_target)
        output_json: Path to write reference_properties.json
        ph: pH for charge calculation
    """
    print(f"[ScoreSequences] Computing reference properties from {existing_peptide_json}...")
    
    data = load_json(existing_peptide_json)
    sequence = data.get("sequence", "")
    
    if not sequence:
        print("  Warning: No sequence found in existing_peptide.json")
        return
        
    props = {
        "sequence": sequence,
        "net_charge": compute_net_charge(sequence, ph),
        "hydrophobic_fraction": hydrophobic_fraction(sequence),
        "aromatic_fraction": aromatic_fraction(sequence),
        "positive_fraction": positive_fraction(sequence),
        "negative_fraction": negative_fraction(sequence),
        "polar_fraction": polar_fraction(sequence),
        "length": sequence_length(sequence)
    }
    
    save_json(props, output_json)
    print(f"[ScoreSequences] Wrote reference properties to {output_json}")
