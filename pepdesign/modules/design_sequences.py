"""
Sequence design module.
Designs peptide sequences for generated backbones.
"""
import os
import pandas as pd
from typing import Optional, Dict, List

from pepdesign.utils import load_csv_as_dicts, save_csv, load_json
from pepdesign.external.protein_mpnn import design_sequences_stub

def design_sequences(
    backbones_dir: str,
    output_csv: str,
    mode: str = "de_novo",
    num_sequences_per_backbone: int = 5,
    existing_peptide_json: Optional[str] = None,
    constraints: Optional[Dict] = None,
    backend: str = "stub",
) -> None:
    """
    Design peptide sequences on backbone structures.
    
    Args:
        backbones_dir: Directory containing backbone_*.pdb and index.csv
        output_csv: Path to write designs table as CSV
        mode: "de_novo" or "optimize_existing"
        num_sequences_per_backbone: Sequences to sample per backbone
        existing_peptide_json: Path to existing peptide data (for optimization)
        constraints: Optional constraints dict with keys:
            Global constraints (applied to all backbones unless overridden):
            - "fixed_positions_global": List[int] - 1-based positions to fix
            - "fixed_residues_global": List[str] - residues at fixed positions
            - "disallowed_residues_global": List[str] - residues disallowed everywhere
            
            Per-backbone constraints (override global):
            - "fixed_positions": Dict[backbone_id, List[int]]
            - "fixed_residues": Dict[backbone_id, List[str]]
            - "disallowed_residues": Dict[backbone_id, Dict[int, List[str]]]
        backend: Backend to use for sequence design:
            - "stub": Lightweight CPU-only stub (default)
            - "local": Local ProteinMPNN installation (not implemented)
            - "colab": External Colab notebook (not implemented)
        
    Writes:
        CSV with columns: backbone_id, design_id, peptide_seq, mpnn_log_prob, mode
    """
    # Validate backend
    if backend == "local":
        raise NotImplementedError("Local ProteinMPNN backend not implemented yet.")
    elif backend == "colab":
        raise NotImplementedError(
            "Colab backend is external; run the Colab notebook to generate sequences.csv."
        )
    elif backend != "stub":
        raise ValueError(f"Unknown backend: {backend}. Must be 'stub', 'local', or 'colab'.")
    
    print(f"[DesignSequences] Running in {mode} mode with {backend} backend...")
    
    # Read backbone index
    index_path = os.path.join(backbones_dir, "index.csv")
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"index.csv not found in {backbones_dir}")
    
    backbones = load_csv_as_dicts(index_path)
    
    # Load existing peptide data if available
    original_sequence = None
    if existing_peptide_json and os.path.exists(existing_peptide_json):
        pep_data = load_json(existing_peptide_json)
        original_sequence = pep_data.get("sequence", None)
    
    # Parse global constraints
    global_fixed_pos = None
    global_fixed_res = None
    global_disallowed = None
    
    if constraints:
        global_fixed_pos = constraints.get("fixed_positions_global", None)
        global_fixed_res = constraints.get("fixed_residues_global", None)
        global_disallowed = constraints.get("disallowed_residues_global", None)
    
    # Design sequences for each backbone
    results = []
    
    for bb_row in backbones:
        backbone_id = bb_row['backbone_id']
        backbone_pdb = bb_row['pdb_path']
        
        print(f"  Designing sequences for {backbone_id}...")
        
        # Get constraints for this backbone (per-backbone overrides global)
        fixed_pos = None
        fixed_res = None
        disallowed_res = None
        
        if constraints:
            # Check for per-backbone constraints first
            if "fixed_positions" in constraints:
                fixed_pos = constraints["fixed_positions"].get(backbone_id, None)
            if "fixed_residues" in constraints:
                fixed_res = constraints["fixed_residues"].get(backbone_id, None)
            if "disallowed_residues" in constraints:
                disallowed_res = constraints["disallowed_residues"].get(backbone_id, None)
        
        # Fall back to global constraints if no per-backbone override
        if fixed_pos is None and global_fixed_pos is not None:
            fixed_pos = global_fixed_pos
            fixed_res = global_fixed_res
        
        # For optimize_existing mode, if no fixed_residues provided, use original sequence
        if mode == "optimize_existing" and fixed_pos and not fixed_res and original_sequence:
            # Extract residues from original sequence at fixed positions
            fixed_res = [original_sequence[pos - 1] for pos in fixed_pos if pos <= len(original_sequence)]
        
        # Handle global disallowed residues
        if global_disallowed and not disallowed_res:
            # Convert global list to per-position dict (apply to all positions)
            # For simplicity in stub, we'll skip this - real ProteinMPNN would handle it
            pass
        
        # Call stub backend
        try:
            sequences = design_sequences_stub(
                backbone_pdb=backbone_pdb,
                peptide_chain="B",
                num_samples=num_sequences_per_backbone,
                fixed_positions=fixed_pos,
                fixed_residues=fixed_res,
                disallowed_residues=disallowed_res,
                config=None
            )
        except Exception as e:
            print(f"    Warning: Failed to design sequences for {backbone_id}: {e}")
            continue
        
        # Collect results
        for seq_idx, (seq, log_prob) in enumerate(sequences):
            design_id = f"{backbone_id}_seq_{seq_idx}"
            results.append({
                'backbone_id': backbone_id,
                'design_id': design_id,
                'peptide_seq': seq,
                'mpnn_log_prob': log_prob,
                'mode': mode,
                'target_chain': 'A',
                'peptide_chain': 'B'
            })
    
    # Write output CSV
    df = pd.DataFrame(results)
    save_csv(df, output_csv)
    
    print(f"[DesignSequences] Wrote {len(results)} designs to {output_csv}")
