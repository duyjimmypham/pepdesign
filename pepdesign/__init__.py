"""
PepDesign - Modular Peptide Design Pipeline

A research-grade pipeline for designing macrocyclic peptide binders.
"""

from pepdesign.modules import (
    prepare_target,
    generate_backbones,
    design_sequences,
    score_sequences,
    rank_sequences,
    compute_reference_properties
)

__version__ = "0.1.0"

__all__ = [
    'prepare_target',
    'generate_backbones',
    'design_sequences',
    'score_sequences',
    'rank_sequences',
    'compute_reference_properties',
]
