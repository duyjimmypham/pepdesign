"""
Sequence scoring module.
Computes physicochemical properties and filters sequences.
Optimized with parallel processing.
"""
import pandas as pd
import numpy as np
from typing import Optional
from pandarallel import pandarallel

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
    Uses parallel processing for speed.
    """
    print(f"[ScoreSequences] Reading sequences from {sequences_csv}...")
    
    # Read input CSV
    df = load_csv(sequences_csv)
    
    if 'peptide_seq' not in df.columns:
        raise ValueError("sequences_csv must contain 'peptide_seq' column")
    
    print(f"[ScoreSequences] Computing physicochemical properties for {len(df)} sequences (Parallel)...")
    
    # Initialize pandarallel
    # verbose=1 shows progress bar
    pandarallel.initialize(progress_bar=True, verbose=1)
    
    # Compute properties using parallel_apply
    df['net_charge'] = df['peptide_seq'].parallel_apply(lambda seq: compute_net_charge(seq, ph))
    df['pI'] = df['peptide_seq'].parallel_apply(estimate_pI)
    df['hydrophobic_fraction'] = df['peptide_seq'].parallel_apply(hydrophobic_fraction)
    df['cys_count'] = df['peptide_seq'].parallel_apply(count_cysteines)
    df['agg_flag'] = df['peptide_seq'].parallel_apply(has_aggregation_motif)
    
    df['length'] = df['peptide_seq'].parallel_apply(sequence_length)
    df['aromatic_fraction'] = df['peptide_seq'].parallel_apply(aromatic_fraction)
    df['positive_fraction'] = df['peptide_seq'].parallel_apply(positive_fraction)
    df['negative_fraction'] = df['peptide_seq'].parallel_apply(negative_fraction)
    df['polar_fraction'] = df['peptide_seq'].parallel_apply(polar_fraction)
    
    # Apply filters (Vectorized)
    mask = pd.Series(True, index=df.index)
    
    if charge_min is not None:
        mask &= (df['net_charge'] >= charge_min)
    
    if charge_max is not None:
        mask &= (df['net_charge'] <= charge_max)
    
    if max_hydrophobic_fraction is not None:
        mask &= (df['hydrophobic_fraction'] <= max_hydrophobic_fraction)
    
    if max_cys_count is not None:
        mask &= (df['cys_count'] <= max_cys_count)
        
    df['passes_filters'] = mask
    
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
    """Compute physicochemical properties for the reference peptide."""
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
