from typing import Any, Dict, Optional
from .base import TargetPrepModule

class SimpleTargetPrep(TargetPrepModule):
    """
    Basic target preparation.
    In v1, this simply records the PDB path and chain ID.
    Future versions could add cleaning, protonation, etc.
    """
    def prepare(self, input_path: str, chain_id: Optional[str] = None) -> Dict[str, Any]:
        print(f"[TargetPrep] Preparing target from {input_path}, chain {chain_id}")
        return {
            "pdb_path": input_path,
            "chain_id": chain_id,
            "status": "ready"
        }
