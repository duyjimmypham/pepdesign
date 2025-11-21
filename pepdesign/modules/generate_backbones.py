"""
Backbone generation module.
Generates macrocyclic peptide backbones positioned at binding site.
"""
import os
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from scipy.spatial.transform import Rotation

from Bio.PDB import Chain, Residue, Atom, Model, Structure

from pepdesign.utils import (
    load_structure,
    save_structure,
    load_json,
    save_csv_from_dicts,
    place_on_circle,
    calculate_centroid,
    get_chain,
    ChainSelect,
)

def _create_macrocycle_chain(
    center: tuple,
    radius: float,
    length: int,
    chain_id: str = "B"
) -> Chain.Chain:
    """Create a simple macrocycle chain of ALAs arranged in a circle."""
    chain = Chain.Chain(chain_id)
    
    # Generate coordinates on circle
    coords = place_on_circle(center, radius, length)
    
    for i, coord in enumerate(coords):
        # Create CA atom
        atom_ca = Atom.Atom(
            "CA",
            np.array(coord, dtype=np.float32),
            20.0,  # B-factor
            1.0,   # Occupancy
            " ",   # Altloc
            " CA ",  # Fullname
            i + 1,  # Serial
            "C"    # Element
        )
        
        # Create residue
        res_id = (' ', i + 1, ' ')
        res = Residue.Residue(res_id, "ALA", " ")
        res.add(atom_ca)
        chain.add(res)
    
    return chain

def _perturb_chain_coordinates(chain: Chain.Chain, translation_std: float = 0.5, rotation_deg: float = 5.0) -> None:
    """
    Apply rigid-body perturbation to chain coordinates in-place.
    
    Args:
        chain: Chain to perturb
        translation_std: Standard deviation for random translation (Angstroms)
        rotation_deg: Standard deviation for random rotation (degrees)
    """
    # Get all atom coordinates
    atoms = list(chain.get_atoms())
    if not atoms:
        return
    
    coords = np.array([atom.get_coord() for atom in atoms])
    
    # Calculate centroid
    centroid = coords.mean(axis=0)
    
    # Center coordinates
    centered_coords = coords - centroid
    
    # Random rotation
    if rotation_deg > 0:
        # Random rotation angles (in radians)
        angles = np.random.normal(0, np.radians(rotation_deg), 3)
        rotation = Rotation.from_euler('xyz', angles)
        centered_coords = rotation.apply(centered_coords)
    
    # Random translation
    translation = np.random.normal(0, translation_std, 3)
    
    # Apply transformation
    new_coords = centered_coords + centroid + translation
    
    # Update atom coordinates
    for atom, new_coord in zip(atoms, new_coords):
        atom.set_coord(new_coord.astype(np.float32))

def generate_backbones(
    target_pdb: str,
    binding_site_json: str,
    output_dir: str,
    num_backbones: int = 10,
    peptide_length: Optional[int] = None,
    mode: str = "stub",
    existing_peptide_json: Optional[str] = None,
) -> Dict[str, any]:
    """
    Generate macrocyclic peptide backbones near binding site.
    
    Args:
        target_pdb: Path to cleaned target PDB
        binding_site_json: Path to binding site metadata
        output_dir: Output directory for backbones
        num_backbones: Number of backbones to generate
        peptide_length: Length of peptide (required for de_novo)
        mode: "stub" or "rfpeptides" (only stub implemented)
        existing_peptide_json: Path to existing peptide data (for optimization)
        
    Returns:
        Dictionary with:
        {
            "backbone_pdbs": [list of paths],
            "index_csv": path to index.csv
        }
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load binding site data
    bs_data = load_json(binding_site_json)
    center = tuple(bs_data["center"])
    
    # Determine peptide length
    if existing_peptide_json:
        pep_data = load_json(existing_peptide_json)
        length = len(pep_data["sequence"])
    elif peptide_length:
        length = peptide_length
    else:
        raise ValueError("Must provide peptide_length for de_novo mode")
    
    if mode == "stub":
        print(f"[GenerateBackbones] Running in STUB mode. Generating {num_backbones} toy backbones.")
        
        backbone_pdbs = []
        index_rows = []
        
        # If optimizing existing peptide, extract real backbone_0
        if existing_peptide_json:
            print(f"  Extracting backbone_0 from existing peptide...")
            pep_data = load_json(existing_peptide_json)
            
            # Load original structure with peptide
            original_pdb = pep_data["original_pdb_path"]
            original_structure = load_structure(original_pdb)
            
            # Extract peptide chain
            peptide_chain_id = pep_data["chain_id"]
            pep_chain = get_chain(original_structure, peptide_chain_id)
            
            if not pep_chain:
                raise ValueError(f"Peptide chain {peptide_chain_id} not found in {original_pdb}")
            
            # Load target structure and add peptide chain
            target_structure = load_structure(target_pdb)
            target_model = target_structure[0]
            
            # Remove existing chain B if present
            if "B" in target_model:
                target_model.detach_child("B")
            
            # Create new chain B from peptide
            new_chain = Chain.Chain("B")
            for i, res_id in enumerate(pep_data["residue_indices"]):
                try:
                    original_res = pep_chain[(' ', res_id, ' ')]
                    # Create new residue with sequential numbering
                    new_res_id = (' ', i + 1, ' ')
                    new_res = Residue.Residue(new_res_id, original_res.get_resname(), " ")
                    
                    # Copy all atoms
                    for atom in original_res:
                        new_atom = atom.copy()
                        new_res.add(new_atom)
                    
                    new_chain.add(new_res)
                except KeyError:
                    print(f"    Warning: Residue {res_id} not found in peptide chain")
                    continue
            
            target_model.add(new_chain)
            
            # Save backbone_0
            backbone_filename = "backbone_0.pdb"
            output_path = os.path.join(output_dir, backbone_filename)
            save_structure(target_structure, output_path)
            
            backbone_pdbs.append(output_path)
            index_rows.append({
                "backbone_id": "backbone_0",
                "pdb_path": output_path,
                "peptide_length": length,
                "mode": "existing",
                "original_sequence": pep_data["sequence"]
            })
            
            # Create perturbed variants
            start_idx = 1
            num_variants = num_backbones - 1
            
            print(f"  Creating {num_variants} perturbed variants...")
            for i in range(start_idx, start_idx + num_variants):
                # Load backbone_0 as template
                perturbed_structure = load_structure(output_path)
                perturbed_model = perturbed_structure[0]
                perturbed_chain = get_chain(perturbed_structure, "B")
                
                # Apply rigid-body perturbation
                _perturb_chain_coordinates(
                    perturbed_chain,
                    translation_std=0.5,  # ±0.5 Å translation
                    rotation_deg=5.0      # ±5° rotation
                )
                
                # Save perturbed backbone
                backbone_filename = f"backbone_{i}.pdb"
                output_path_perturbed = os.path.join(output_dir, backbone_filename)
                save_structure(perturbed_structure, output_path_perturbed)
                
                backbone_pdbs.append(output_path_perturbed)
                index_rows.append({
                    "backbone_id": f"backbone_{i}",
                    "pdb_path": output_path_perturbed,
                    "peptide_length": length,
                    "mode": "perturbed",
                    "original_sequence": pep_data["sequence"]
                })
        else:
            # De novo mode: generate abstract macrocycles
            for i in range(num_backbones):
                # Load target structure
                structure = load_structure(target_pdb)
                model = structure[0]
                
                # Vary radius for diversity
                radius = 5.0 + np.random.uniform(-0.5, 0.5)
                
                # Create macrocycle chain
                pep_chain = _create_macrocycle_chain(center, radius, length, chain_id="B")
                
                # Add to model
                if "B" in model:
                    model.detach_child("B")
                model.add(pep_chain)
                
                # Save
                backbone_filename = f"backbone_{i}.pdb"
                output_path = os.path.join(output_dir, backbone_filename)
                save_structure(structure, output_path)
                
                backbone_pdbs.append(output_path)
                index_rows.append({
                    "backbone_id": f"backbone_{i}",
                    "pdb_path": output_path,
                    "peptide_length": length,
                    "mode": "stub"
                })
        
        # Write index CSV
        index_csv = os.path.join(output_dir, "index.csv")
        fieldnames = ["backbone_id", "pdb_path", "peptide_length", "mode"]
        if existing_peptide_json:
            fieldnames.append("original_sequence")
        
        save_csv_from_dicts(index_rows, index_csv, fieldnames=fieldnames)
        
        return {
            "backbone_pdbs": backbone_pdbs,
            "index_csv": index_csv
        }
    
    elif mode == "rfpeptides":
        # Placeholder for real RFpeptides integration
        from pepdesign.external.rfpeptides import run_rfpeptides
        raise NotImplementedError("RFpeptides backend not yet implemented")
    
    else:
        raise ValueError(f"Unknown mode: {mode}")
