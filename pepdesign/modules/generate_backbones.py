"""
Backbone generation module.
Generates macrocyclic peptide backbones positioned at binding site.
"""
import os
import numpy as np
from typing import Dict, List, Optional, Any
from scipy.spatial.transform import Rotation

from Bio.PDB import Chain, Residue, Atom, Model, Structure

from pepdesign.interfaces import BackboneGenerator, BackboneResult
from pepdesign.config import BackboneConfig
from pepdesign.utils import (
    load_structure,
    save_structure,
    load_json,
    save_csv_from_dicts,
    place_on_circle,
    calculate_centroid,
    get_chain,
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
    """Apply rigid-body perturbation to chain coordinates in-place."""
    atoms = list(chain.get_atoms())
    if not atoms:
        return
    
    coords = np.array([atom.get_coord() for atom in atoms])
    centroid = coords.mean(axis=0)
    centered_coords = coords - centroid
    
    if rotation_deg > 0:
        angles = np.random.normal(0, np.radians(rotation_deg), 3)
        rotation = Rotation.from_euler('xyz', angles)
        centered_coords = rotation.apply(centered_coords)
    
    translation = np.random.normal(0, translation_std, 3)
    new_coords = centered_coords + centroid + translation
    
    for atom, new_coord in zip(atoms, new_coords):
        atom.set_coord(new_coord.astype(np.float32))

class StubBackboneGenerator(BackboneGenerator):
    """
    Stub implementation of backbone generation.
    Generates toy macrocycles or perturbs existing peptides.
    """
    
    def generate(
        self,
        target_pdb: str,
        binding_site_data: Dict[str, Any],
        output_dir: str,
        config: BackboneConfig,
        existing_peptide_data: Dict[str, Any] = None
    ) -> List[BackboneResult]:
        
        print(f"[StubBackboneGenerator] Generating {config.num_backbones} backbones...")
        os.makedirs(output_dir, exist_ok=True)
        
        center = tuple(binding_site_data["center"])
        results = []
        
        # Determine peptide length
        if existing_peptide_data:
            length = len(existing_peptide_data["sequence"])
        elif config.peptide_length:
            length = config.peptide_length
        else:
            raise ValueError("Must provide peptide_length for de_novo mode")

        # Mode: Optimize Existing (Perturbation)
        if existing_peptide_data:
            print(f"  Extracting backbone_0 from existing peptide...")
            
            original_pdb = existing_peptide_data["original_pdb_path"]
            original_structure = load_structure(original_pdb)
            peptide_chain_id = existing_peptide_data["chain_id"]
            pep_chain = get_chain(original_structure, peptide_chain_id)
            
            if not pep_chain:
                raise ValueError(f"Peptide chain {peptide_chain_id} not found in {original_pdb}")
            
            # Load target structure
            target_structure = load_structure(target_pdb)
            target_model = target_structure[0]
            
            # Remove existing chain B if present (TODO: Parameterize this)
            target_peptide_chain_id = "B" 
            if target_peptide_chain_id in target_model:
                target_model.detach_child(target_peptide_chain_id)
            
            # Create new chain from peptide
            new_chain = Chain.Chain(target_peptide_chain_id)
            for i, res_id in enumerate(existing_peptide_data["residue_indices"]):
                try:
                    original_res = pep_chain[(' ', res_id, ' ')]
                    new_res_id = (' ', i + 1, ' ')
                    new_res = Residue.Residue(new_res_id, original_res.get_resname(), " ")
                    for atom in original_res:
                        new_res.add(atom.copy())
                    new_chain.add(new_res)
                except KeyError:
                    continue
            
            target_model.add(new_chain)
            
            # Save backbone_0
            backbone_0_path = os.path.join(output_dir, "backbone_0.pdb")
            save_structure(target_structure, backbone_0_path)
            
            results.append(BackboneResult(
                backbone_id="backbone_0",
                pdb_path=backbone_0_path,
                peptide_chain_id=target_peptide_chain_id,
                metadata={"mode": "existing", "original_sequence": existing_peptide_data["sequence"]}
            ))
            
            # Generate perturbations
            for i in range(1, config.num_backbones):
                perturbed_structure = load_structure(backbone_0_path)
                perturbed_chain = get_chain(perturbed_structure, target_peptide_chain_id)
                
                _perturb_chain_coordinates(
                    perturbed_chain,
                    translation_std=config.translation_std,
                    rotation_deg=config.rotation_deg
                )
                
                path = os.path.join(output_dir, f"backbone_{i}.pdb")
                save_structure(perturbed_structure, path)
                
                results.append(BackboneResult(
                    backbone_id=f"backbone_{i}",
                    pdb_path=path,
                    peptide_chain_id=target_peptide_chain_id,
                    metadata={"mode": "perturbed", "original_sequence": existing_peptide_data["sequence"]}
                ))
                
        # Mode: De Novo (Toy Macrocycles)
        else:
            target_peptide_chain_id = "B"
            for i in range(config.num_backbones):
                structure = load_structure(target_pdb)
                model = structure[0]
                
                radius = 5.0 + np.random.uniform(-0.5, 0.5)
                pep_chain = _create_macrocycle_chain(center, radius, length, chain_id=target_peptide_chain_id)
                
                if target_peptide_chain_id in model:
                    model.detach_child(target_peptide_chain_id)
                model.add(pep_chain)
                
                path = os.path.join(output_dir, f"backbone_{i}.pdb")
                save_structure(structure, path)
                
                results.append(BackboneResult(
                    backbone_id=f"backbone_{i}",
                    pdb_path=path,
                    peptide_chain_id=target_peptide_chain_id,
                    metadata={"mode": "stub_denovo"}
                ))
        
        # Write index CSV for record keeping
        index_rows = [
            {
                "backbone_id": r.backbone_id,
                "pdb_path": r.pdb_path,
                "peptide_chain_id": r.peptide_chain_id,
                **r.metadata
            }
            for r in results
        ]
        fieldnames = ["backbone_id", "pdb_path", "peptide_chain_id", "mode", "original_sequence"]
        save_csv_from_dicts(index_rows, os.path.join(output_dir, "index.csv"), fieldnames=fieldnames)
        
        return results

# Factory function to get generator
def get_backbone_generator(config: BackboneConfig) -> BackboneGenerator:
    if config.generator_type == "stub":
        return StubBackboneGenerator()
    elif config.generator_type == "rfdiffusion":
        raise NotImplementedError("RFdiffusion generator not yet implemented")
    else:
        raise ValueError(f"Unknown generator type: {config.generator_type}")
