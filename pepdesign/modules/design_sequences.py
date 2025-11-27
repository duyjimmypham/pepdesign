"""
Sequence design module.
Designs peptide sequences for generated backbones.
"""
import os
import pandas as pd
import random
from typing import Dict, List, Any, Tuple

from pepdesign.interfaces import SequenceDesigner, DesignResult, BackboneResult
from pepdesign.config import DesignConfig
from pepdesign.utils import load_structure, get_chain, save_csv

class StubSequenceDesigner(SequenceDesigner):
    """
    Stub implementation of sequence design.
    Generates random sequences or mutates existing ones.
    """
    
    def design(
        self,
        backbone_results: List[BackboneResult],
        output_dir: str,
        config: DesignConfig,
        global_constraints: Dict[str, Any] = None
    ) -> List[DesignResult]:
        
        print(f"[StubSequenceDesigner] Designing sequences for {len(backbone_results)} backbones...")
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        aa_alphabet = "ACDEFGHIKLMNPQRSTVWY"
        
        for bb in backbone_results:
            # Determine constraints
            fixed_pos = []
            fixed_res = []
            
            if global_constraints:
                fixed_pos = global_constraints.get("fixed_positions_global") or []
                fixed_res = global_constraints.get("fixed_residues_global") or []
            
            # If optimizing existing, fix residues if not specified otherwise
            if bb.metadata.get("mode") in ["existing", "perturbed"] and not fixed_pos:
                # In a real scenario, we might fix hot-spots here.
                # For stub, we'll just use the original sequence as a bias if available
                pass

            # Get sequence length from PDB
            structure = load_structure(bb.pdb_path)
            chain = get_chain(structure, bb.peptide_chain_id)
            if not chain:
                print(f"Warning: Chain {bb.peptide_chain_id} not found in {bb.pdb_path}")
                continue
            length = len(list(chain))
            
            # Generate sequences
            for i in range(config.num_sequences_per_backbone):
                seq_chars = []
                for pos in range(1, length + 1):
                    if pos in fixed_pos:
                        idx = fixed_pos.index(pos)
                        if idx < len(fixed_res):
                            seq_chars.append(fixed_res[idx])
                        else:
                            seq_chars.append(random.choice(aa_alphabet))
                    else:
                        seq_chars.append(random.choice(aa_alphabet))
                
                sequence = "".join(seq_chars)
                log_prob = -float(length) + random.uniform(-2.0, 2.0)
                
                design_id = f"{bb.backbone_id}_seq_{i}"
                
                results.append(DesignResult(
                    design_id=design_id,
                    backbone_id=bb.backbone_id,
                    sequence=sequence,
                    score=log_prob,
                    metadata={"mode": "stub", "mpnn_log_prob": log_prob, "pdb_path": bb.pdb_path}
                ))
        
        # Save results to CSV
        csv_rows = [
            {
                "design_id": r.design_id,
                "backbone_id": r.backbone_id,
                "peptide_seq": r.sequence,
                "score": r.score,
                **r.metadata
            }
            for r in results
        ]
        save_csv(pd.DataFrame(csv_rows), os.path.join(output_dir, "sequences.csv"))
        
        return results

# Factory function
def get_sequence_designer(config: DesignConfig) -> SequenceDesigner:
    if config.designer_type == "stub":
        return StubSequenceDesigner()
    elif config.designer_type == "protein_mpnn":
        from pepdesign.external.protein_mpnn import ProteinMPNNDesigner
        return ProteinMPNNDesigner()
    else:
        raise ValueError(f"Unknown designer type: {config.designer_type}")
