from typing import Any, Dict, List
from .base import ScoringModule, RankingModule

class BasicScorer(ScoringModule):
    """
    Basic scorer that uses pLDDT from the structure prediction.
    """
    def score(self, structure_info: Dict[str, Any]) -> float:
        # In a real scenario, this might calculate dG, interface energy, etc.
        # Here we just return the pLDDT from the prediction step.
        score = structure_info.get("plddt", 0.0)
        print(f"[Scoring] Scored {structure_info['id']}: {score}")
        return score


