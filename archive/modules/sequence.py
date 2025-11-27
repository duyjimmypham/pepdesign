from typing import Any, Dict, List
from .base import SequenceDesignerModule
import random

class ProteinMPNNStub(SequenceDesignerModule):
    """
    Stub for ProteinMPNN sequence design.
    """
    def design(self, backbone_info: Dict[str, Any], num_sequences: int = 1) -> List[Dict[str, Any]]:
        print(f"[Sequence] Designing {num_sequences} sequences for backbone {backbone_info['id']}...")
        designs = []
        aa_code = "ACDEFGHIKLMNPQRSTVWY"
        for i in range(num_sequences):
            # Random sequence of length 10 for demo
            seq = "".join(random.choice(aa_code) for _ in range(10))
            designs.append({
                "id": f"{backbone_info['id']}_seq_{i}",
                "backbone_id": backbone_info["id"],
                "sequence": seq,
                "source": "ProteinMPNN_stub"
            })
        return designs
