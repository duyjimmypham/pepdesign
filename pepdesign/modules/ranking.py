"""
Ranking module.
Ranks designed sequences based on composite scores.
"""
import pandas as pd
from typing import Optional

from pepdesign.utils import load_csv, save_csv, load_json

def rank_sequences(
    scored_csv: str,
    output_csv: str,
    weight_charge: float = 0.3,
    weight_hydrophobic: float = 0.3,
    weight_filters: float = 0.4,
    reference_properties_json: Optional[str] = None,
) -> None:
    """
    Rank sequences based on composite score.
    
    Composite score formula:
    - Sequences that fail filters get score = 0
    - For passing sequences:
      score = weight_filters * 1.0 
            + weight_charge * (1 - abs(net_charge) / 10)  # Prefer near-neutral
            + weight_hydrophobic * (1 - hydrophobic_fraction)  # Prefer less hydrophobic
    
    Args:
        scored_csv: Input CSV with scored sequences
        output_csv: Output CSV with added 'composite_score' and 'rank' columns
        weight_charge: Weight for charge component (default 0.3)
        weight_hydrophobic: Weight for hydrophobic component (default 0.3)
        weight_filters: Weight for passing filters (default 0.4)
    """
    print(f"[RankSequences] Reading scored sequences from {scored_csv}...")
    
    df = load_csv(scored_csv)
    
    # Check required columns
    required_cols = ['passes_filters', 'net_charge', 'hydrophobic_fraction']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    print(f"[RankSequences] Computing composite scores for {len(df)} sequences...")
    
    # Initialize composite score
    df['composite_score'] = 0.0
    
    # Compute score for sequences that pass filters
    passing_mask = df['passes_filters'] == True
    
    if passing_mask.sum() > 0:
        # Check for reference properties
        ref_props = None
        if reference_properties_json:
            try:
                ref_props = load_json(reference_properties_json)
                print(f"[RankSequences] Using reference properties from {reference_properties_json}")
            except Exception as e:
                print(f"[RankSequences] Warning: Failed to load reference properties: {e}")
        
        # Calculate penalties if reference available
        penalty_charge = 0.0
        penalty_hydro = 0.0
        penalty_aromatic = 0.0
        
        if ref_props:
            # Charge penalty: difference from reference
            ref_charge = ref_props.get('net_charge', 0.0)
            penalty_charge = (df.loc[passing_mask, 'net_charge'] - ref_charge).abs() / 10.0
            penalty_charge = penalty_charge.clip(0, 1)
            
            # Hydrophobic penalty: difference from reference
            ref_hydro = ref_props.get('hydrophobic_fraction', 0.0)
            penalty_hydro = (df.loc[passing_mask, 'hydrophobic_fraction'] - ref_hydro).abs()
            
            # Aromatic penalty: difference from reference
            ref_aromatic = ref_props.get('aromatic_fraction', 0.0)
            if 'aromatic_fraction' in df.columns:
                penalty_aromatic = (df.loc[passing_mask, 'aromatic_fraction'] - ref_aromatic).abs()
        
        # Component scores (1.0 is best, 0.0 is worst)
        if ref_props:
            # Target-aware scoring
            score_charge = 1.0 - penalty_charge
            score_hydro = 1.0 - penalty_hydro
            score_aromatic = 1.0 - penalty_aromatic
            
            # Composite score with reference
            # Re-distribute weights to include aromatic
            w_total = weight_charge + weight_hydrophobic
            w_c = weight_charge / w_total * (weight_charge + weight_hydrophobic) if w_total > 0 else 0
            w_h = weight_hydrophobic / w_total * (weight_charge + weight_hydrophobic) if w_total > 0 else 0
            
            # Simple equal weighting for now if not specified
            # Let's use the provided weights for charge/hydro and add aromatic with same weight as hydro
            # Normalized to sum to (1 - weight_filters)
            
            remaining_weight = 1.0 - weight_filters
            # Split remaining weight equally among 3 components
            w_c = remaining_weight / 3
            w_h = remaining_weight / 3
            w_a = remaining_weight / 3
            
            df.loc[passing_mask, 'composite_score'] = (
                weight_filters * 1.0 +
                w_c * score_charge +
                w_h * score_hydro +
                w_a * score_aromatic
            )
        else:
            # Original generic scoring
            charge_component = 1.0 - (df.loc[passing_mask, 'net_charge'].abs() / 10.0).clip(0, 1)
            hydro_component = 1.0 - df.loc[passing_mask, 'hydrophobic_fraction'].clip(0, 1)
            
            df.loc[passing_mask, 'composite_score'] = (
                weight_filters * 1.0 +
                weight_charge * charge_component +
                weight_hydrophobic * hydro_component
            )
    
    # Rank by composite score (descending)
    df = df.sort_values('composite_score', ascending=False)
    df['rank'] = range(1, len(df) + 1)
    
    # Save ranked sequences
    save_csv(df, output_csv)
    
    num_passing = passing_mask.sum()
    print(f"[RankSequences] Wrote {len(df)} ranked sequences to {output_csv}")
    print(f"  - Sequences passing filters: {num_passing}")
    if num_passing > 0:
        print(f"  - Top score: {df.iloc[0]['composite_score']:.3f}")
        print(f"  - Top sequence: {df.iloc[0].get('design_id', 'N/A')}")
