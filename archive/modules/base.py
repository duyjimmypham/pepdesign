from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional

class TargetPrepModule(ABC):
    """Prepares the target protein for docking/design."""
    @abstractmethod
    def prepare(self, input_path: str, chain_id: Optional[str] = None) -> Dict[str, Any]:
        pass

class BackboneGeneratorModule(ABC):
    """Generates peptide backbones."""
    @abstractmethod
    def generate(self, target_info: Dict[str, Any], num_backbones: int = 1) -> List[Dict[str, Any]]:
        pass

class SequenceDesignerModule(ABC):
    """Designs sequences for a given backbone."""
    @abstractmethod
    def design(self, backbone_info: Dict[str, Any], num_sequences: int = 1) -> List[Dict[str, Any]]:
        pass

class StructurePredictorModule(ABC):
    """Predicts structure of peptide-protein complex."""
    @abstractmethod
    def predict(self, sequence_info: Dict[str, Any], target_info: Dict[str, Any]) -> Dict[str, Any]:
        pass

class ScoringModule(ABC):
    """Scores a designed peptide structure."""
    @abstractmethod
    def score(self, structure_info: Dict[str, Any]) -> float:
        pass

class RankingModule(ABC):
    """Ranks designs based on scores."""
    @abstractmethod
    def rank(self, scored_designs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass
