"""
PDB utility functions for structure manipulation.
Centralizes all PDB I/O and cleaning operations.
"""
import os
from typing import Optional, List, Set
from Bio.PDB import PDBParser, PDBIO, Select, Structure, Chain, Residue
from Bio.PDB.Polypeptide import is_aa

class ChainSelect(Select):
    """Select specific chain(s) from structure."""
    def __init__(self, chain_ids: Set[str]):
        self.chain_ids = chain_ids
    
    def accept_chain(self, chain: Chain.Chain) -> int:
        return 1 if chain.id in self.chain_ids else 0

class CleanSelect(Select):
    """Select and clean structure: remove waters, keep specified cofactors."""
    def __init__(self, chain_id: str, keep_cofactors: Optional[List[str]] = None):
        self.chain_id = chain_id
        self.keep_cofactors = set(keep_cofactors) if keep_cofactors else set()
        self.common_metals = {"ZN", "MG", "CA", "FE", "MN", "CO", "NI", "CU"}
    
    def accept_chain(self, chain: Chain.Chain) -> int:
        return 1 if chain.id == self.chain_id else 0
    
    def accept_residue(self, residue: Residue.Residue) -> int:
        resname = residue.get_resname().strip()
        # Remove waters
        if resname == "HOH":
            return 0
        # Keep standard amino acids
        if is_aa(residue, standard=True):
            return 1
        # Keep specified cofactors
        if resname in self.keep_cofactors:
            return 1
        # Keep common metals
        if resname in self.common_metals:
            return 1
        return 0

def load_structure(pdb_path: str, name: str = "structure", quiet: bool = True) -> Structure.Structure:
    """Load PDB structure."""
    parser = PDBParser(QUIET=quiet)
    return parser.get_structure(name, pdb_path)

def save_structure(structure: Structure.Structure, output_path: str, select: Optional[Select] = None) -> None:
    """Save PDB structure."""
    io = PDBIO()
    io.set_structure(structure)
    if select:
        io.save(output_path, select=select)
    else:
        io.save(output_path)

def remove_altlocs(structure: Structure.Structure, chain_id: Optional[str] = None) -> None:
    """
    Remove alternate locations, keeping highest occupancy or 'A'.
    Modifies structure in-place.
    """
    for model in structure:
        for chain in model:
            if chain_id and chain.id != chain_id:
                continue
            for residue in chain:
                if residue.is_disordered():
                    disordered_atoms = [atom for atom in residue if atom.is_disordered()]
                    for atom in disordered_atoms:
                        children = atom.disordered_get_list()
                        # Sort by occupancy (desc), then prefer 'A'
                        children.sort(
                            key=lambda a: (a.get_occupancy(), 1 if a.get_altloc() == 'A' else 0),
                            reverse=True
                        )
                        best = children[0]
                        atom.disordered_select(best.get_altloc())

def get_chain(structure: Structure.Structure, chain_id: str) -> Optional[Chain.Chain]:
    """Get specific chain from structure."""
    model = structure[0]
    return model[chain_id] if chain_id in model else None

def get_residue_atoms(chain: Chain.Chain, residue_ids: List[int]) -> List:
    """Get all atoms from specified residues."""
    atoms = []
    for resid in residue_ids:
        try:
            res = chain[(' ', resid, ' ')]
            atoms.extend(res.get_atoms())
        except KeyError:
            pass
    return atoms

def get_ca_atoms(chain: Chain.Chain, residue_ids: Optional[List[int]] = None) -> List:
    """Get CA atoms from chain or specified residues."""
    ca_atoms = []
    if residue_ids:
        for resid in residue_ids:
            try:
                res = chain[(' ', resid, ' ')]
                if 'CA' in res:
                    ca_atoms.append(res['CA'])
            except KeyError:
                pass
    else:
        for residue in chain:
            if 'CA' in residue:
                ca_atoms.append(residue['CA'])
    return ca_atoms
