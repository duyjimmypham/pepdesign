from typing import Any, Dict, List
from .base import RankingModule

class SimpleRanker(RankingModule):
    """
    Ranks designs by score (descending).
    """
    def rank(self, scored_designs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        print(f"[Ranking] Ranking {len(scored_designs)} designs...")
        # Sort by score descending
        return sorted(scored_designs, key=lambda x: x.get("score", 0.0), reverse=True)
