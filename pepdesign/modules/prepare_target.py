"""
Target preparation module.
Cleans PDB structure and identifies binding site.
"""
import os
import warnings
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple, Dict

from Bio.PDB import NeighborSearch
from Bio.PDB.Polypeptide import is_aa

from pepdesign.models import TargetState, BindingSiteModel, PeptideInfo

# Import centralized utilities
from pepdesign.utils import (
    load_structure,
    save_structure,
    remove_altlocs,
    get_chain,
    get_ca_atoms,
    get_residue_atoms,
    calculate_centroid,
    load_json,
    save_json,
    CleanSelect,
)

# Fallback for three_to_one
try:
    from Bio.PDB.Polypeptide import three_to_one
except ImportError:
    try:
        from Bio.SeqUtils import seq1 as three_to_one
    except ImportError:
        def three_to_one(s):
            d = {'ALA':'A', 'CYS':'C', 'ASP':'D', 'GLU':'E', 'PHE':'F',
                 'GLY':'G', 'HIS':'H', 'ILE':'I', 'LYS':'K', 'LEU':'L',
                 'MET':'M', 'ASN':'N', 'PRO':'P', 'GLN':'Q', 'ARG':'R',
                 'SER':'S', 'THR':'T', 'VAL':'V', 'TRP':'W', 'TYR':'Y'}
            return d.get(s.upper(), 'X')

@dataclass
class BindingSite:
    chain_id: str
    residue_indices: List[int]
    center: Tuple[float, float, float]
    radius: float
    source: str

def prepare_target(
    pdb_path: str,
    output_dir: str,
    mode: str = "de_novo",
    target_chain: Optional[str] = None,
    binding_site_residues: Optional[List[int]] = None,
    peptide_chain: Optional[str] = None,
    contact_cutoff: float = 5.0,
    keep_cofactors: Optional[List[str]] = None,
    do_relax: bool = True
) -> TargetState:
    """
    Prepare cleaned target structure and binding-site metadata.
    
    Args:
        pdb_path: Path to input PDB file
        output_dir: Output directory for cleaned files
        mode: "de_novo" or "optimize_existing"
        target_chain: Target protein chain ID
        binding_site_residues: Manual binding site residues (for de_novo)
        peptide_chain: Peptide chain ID (for optimize_existing)
        contact_cutoff: Distance cutoff for binding site detection (Å)
        keep_cofactors: List of cofactor residue names to keep
        do_relax: Whether to run RosettaRelax
        
    Returns:
        TargetState object
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load and clean structure
    structure = load_structure(pdb_path)
    remove_altlocs(structure, target_chain)
    
    # Save cleaned structure
    clean_pdb_path = os.path.join(output_dir, "target_clean.pdb")
    save_structure(structure, clean_pdb_path, select=CleanSelect(target_chain, keep_cofactors))
    
    # Reload for binding site analysis
    clean_structure = load_structure(clean_pdb_path)
    target_chain_obj = get_chain(clean_structure, target_chain)
    
    if not target_chain_obj:
        raise ValueError(f"Chain {target_chain} not found in structure")
    
    # Initialize binding site data
    bs_residues: List[int] = []
    bs_center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    bs_radius: float = 8.0
    bs_source: str = "unknown"
    peptide_info: Optional[PeptideInfo] = None
    
    if mode == "optimize_existing":
        if not peptide_chain:
            raise ValueError("peptide_chain is required for optimize_existing mode")
        
        pep_chain_obj = get_chain(structure, peptide_chain)
        if not pep_chain_obj:
            raise ValueError(f"Peptide chain {peptide_chain} not found in {pdb_path}")
        
        # Find binding site residues by proximity
        pep_atoms = list(pep_chain_obj.get_atoms())
        target_atoms = list(target_chain_obj.get_atoms())
        ns = NeighborSearch(target_atoms)
        
        nearby_residues_set = set()
        for patom in pep_atoms:
            close_residues = ns.search(patom.get_coord(), contact_cutoff, level='R')
            for res in close_residues:
                if res.get_parent().id == target_chain:
                    nearby_residues_set.add(res.id[1])
        
        bs_residues = sorted(list(nearby_residues_set))
        
        # Calculate center from peptide CA atoms
        pep_ca_atoms = [a for a in pep_atoms if a.get_name() == "CA"]
        if not pep_ca_atoms:
            pep_ca_atoms = pep_atoms
        bs_center = calculate_centroid([a.get_coord() for a in pep_ca_atoms])
        bs_source = "from_peptide"
        
        # Extract existing peptide sequence
        pep_seq = ""
        pep_res_indices = []
        for res in pep_chain_obj:
            if is_aa(res, standard=True):
                try:
                    pep_seq += three_to_one(res.get_resname())
                    pep_res_indices.append(res.id[1])
                except KeyError:
                    pass
        
        peptide_info = PeptideInfo(
            chain_id=peptide_chain,
            sequence=pep_seq,
            residue_indices=pep_res_indices,
            original_pdb_path=pdb_path
        )
        
    elif mode == "de_novo":
        if binding_site_residues:
            # Manual binding site
            bs_residues = binding_site_residues
            valid_ids = {r.id[1] for r in target_chain_obj}
            missing = [r for r in bs_residues if r not in valid_ids]
            if missing:
                warnings.warn(f"Residues {missing} not found in target chain")
            
            # Calculate center from CA atoms
            ca_atoms = get_ca_atoms(target_chain_obj, bs_residues)
            if ca_atoms:
                bs_center = calculate_centroid([a.get_coord() for a in ca_atoms])
            bs_source = "manual"
        else:
            # Auto-detect pocket (stub)
            print("[INFO] Auto-detecting pocket (STUB)...")
            residues = list(target_chain_obj)
            mid = len(residues) // 2
            subset = residues[max(0, mid-3):min(len(residues), mid+3)]
            bs_residues = [r.id[1] for r in subset]
            
            ca_atoms = [r['CA'] for r in subset if 'CA' in r]
            if ca_atoms:
                bs_center = calculate_centroid([a.get_coord() for a in ca_atoms])
            bs_source = "auto_stub"
    else:
        raise ValueError(f"Unknown mode: {mode}")
    
    # Create BindingSiteModel
    bs_model = BindingSiteModel(
        chain_id=target_chain,
        residue_indices=bs_residues,
        center=bs_center,
        radius=bs_radius,
        source=bs_source
    )
    
    # Save binding site metadata
    binding_site_json = os.path.join(output_dir, "binding_site.json")
    save_json(bs_model.dict(), binding_site_json)
    
    # Relaxation Step
    relaxed_pdb_path = None
    if do_relax:
        # Use OpenMM by default as requested
        from pepdesign.external.openmm import get_openmm_relaxer
        relaxer = get_openmm_relaxer()
        relaxed_pdb_path = os.path.join(output_dir, "target_relaxed.pdb")
        try:
            relaxer.relax(clean_pdb_path, relaxed_pdb_path)
        except Exception as e:
            print(f"[Warning] OpenMM Relaxation failed: {e}")
            # Fallback to Rosetta? Or just fail? 
            # User said "Keep RosettaRelaxer for now for future integration", implying OpenMM is the primary.
            # We'll just log warning and continue without relaxation if it fails.
            relaxed_pdb_path = None

    return TargetState(
        pdb_path=clean_pdb_path,
        relaxed_pdb_path=relaxed_pdb_path,
        binding_site=bs_model,
        sequence=None, # Could extract sequence here if needed
        peptide_info=peptide_info
    )
