"""
Utility modules for peptide design pipeline.
"""
from .pdb_utils import (
    load_structure,
    save_structure,
    remove_altlocs,
    get_chain,
    get_residue_atoms,
    get_ca_atoms,
    CleanSelect,
    ChainSelect,
)

from .chemistry import (
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
)

from .geometry import (
    calculate_centroid,
    calculate_distance,
    place_on_circle,
)

from .io_utils import (
    load_json,
    save_json,
    load_csv,
    save_csv,
    load_csv_as_dicts,
    save_csv_from_dicts,
)

__all__ = [
    # PDB utils
    'load_structure',
    'save_structure',
    'remove_altlocs',
    'get_chain',
    'get_residue_atoms',
    'get_ca_atoms',
    'CleanSelect',
    'ChainSelect',
    # Chemistry
    'compute_net_charge',
    'estimate_pI',
    'hydrophobic_fraction',
    'count_cysteines',
    'has_aggregation_motif',
    'sequence_length',
    'aromatic_fraction',
    'positive_fraction',
    'negative_fraction',
    'polar_fraction',
    # Geometry
    'calculate_centroid',
    'calculate_distance',
    'place_on_circle',
    # I/O
    'load_json',
    'save_json',
    'load_csv',
    'save_csv',
    'load_csv_as_dicts',
    'save_csv_from_dicts',
]
