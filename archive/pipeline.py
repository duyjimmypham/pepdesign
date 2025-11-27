from typing import Dict, Any, Optional, List
from .modules.base import (
    TargetPrepModule, BackboneGeneratorModule, SequenceDesignerModule,
    StructurePredictorModule, ScoringModule, RankingModule
)
from .modules.target import SimpleTargetPrep
from .modules.backbone import RFPeptidesStub
from .modules.sequence import ProteinMPNNStub
from .modules.structure import ColabFoldStub
from .modules.scoring import BasicScorer
from .modules.ranking import SimpleRanker

class PeptideDesignPipeline:
    def __init__(self, 
                 target_prep: Optional[TargetPrepModule] = None,
                 backbone_gen: Optional[BackboneGeneratorModule] = None,
                 seq_designer: Optional[SequenceDesignerModule] = None,
                 struct_pred: Optional[StructurePredictorModule] = None,
                 scorer: Optional[ScoringModule] = None,
                 ranker: Optional[RankingModule] = None):
        
        # Use defaults if not provided
        self.target_prep = target_prep or SimpleTargetPrep()
        self.backbone_gen = backbone_gen or RFPeptidesStub()
        self.seq_designer = seq_designer or ProteinMPNNStub()
        self.struct_pred = struct_pred or ColabFoldStub()
        self.scorer = scorer or BasicScorer()
        self.ranker = ranker or SimpleRanker()

    def run_de_novo(self, target_pdb: str, chain_id: str, num_designs: int = 5) -> List[Dict[str, Any]]:
        """
        Runs the de novo design pipeline.
        1. Prepare Target
        2. Generate Backbones
        3. Design Sequences
        4. Predict Structures
        5. Score
        6. Rank
        """
        print("=== Starting De Novo Design Pipeline ===")
        
        # 1. Prepare Target
        target_info = self.target_prep.prepare(target_pdb, chain_id)
        
        # 2. Generate Backbones
        backbones = self.backbone_gen.generate(target_info, num_backbones=num_designs)
        
        scored_designs = []
        
        for bb in backbones:
            # 3. Design Sequences (1 sequence per backbone for simplicity in v1)
            sequences = self.seq_designer.design(bb, num_sequences=1)
            
            for seq in sequences:
                # 4. Predict Structure
                structure = self.struct_pred.predict(seq, target_info)
                
                # 5. Score
                score = self.scorer.score(structure)
                
                design_result = {
                    **seq,
                    "structure": structure,
                    "score": score
                }
                scored_designs.append(design_result)
        
        # 6. Rank
        ranked_designs = self.ranker.rank(scored_designs)
        
        print(f"=== Pipeline Completed. Top score: {ranked_designs[0]['score']} ===")
        return ranked_designs

    def run_optimization(self, target_pdb: str, peptide_pdb: str, chain_id: str) -> List[Dict[str, Any]]:
        """
        Runs the optimization pipeline.
        (Placeholder for v1 - reuses sequence design on existing backbone)
        """
        print("=== Starting Optimization Pipeline ===")
        # In a real scenario, we'd extract the backbone from peptide_pdb
        # For now, we'll simulate it by creating a mock backbone info
        
        target_info = self.target_prep.prepare(target_pdb, chain_id)
        
        mock_backbone = {
            "id": "existing_peptide_bb",
            "source": peptide_pdb
        }
        
        # Optimize sequence on this backbone
        sequences = self.seq_designer.design(mock_backbone, num_sequences=5)
        
        scored_designs = []
        for seq in sequences:
            structure = self.struct_pred.predict(seq, target_info)
            score = self.scorer.score(structure)
            scored_designs.append({**seq, "structure": structure, "score": score})
            
        return self.ranker.rank(scored_designs)
