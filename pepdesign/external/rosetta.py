"""
Rosetta wrapper for structure relaxation and scoring.
Supports PyRosetta (preferred) and Rosetta binaries.
"""
from abc import ABC, abstractmethod
import os
from typing import Optional

class RosettaRelaxer(ABC):
    """Abstract base class for Rosetta relaxation."""
    
    @abstractmethod
    def relax(self, pdb_path: str, output_path: str) -> str:
        """
        Relax the input PDB structure.
        
        Args:
            pdb_path: Path to input PDB
            output_path: Path to save relaxed PDB
            
        Returns:
            Path to the relaxed PDB (should match output_path)
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this relaxer is operational."""
        pass

class PyRosettaRelaxer(RosettaRelaxer):
    """
    Uses PyRosetta for FastRelax.
    Requires `pyrosetta` to be installed.
    """
    def __init__(self):
        self._available = False
        try:
            import pyrosetta
            from pyrosetta import rosetta
            self._available = True
        except ImportError:
            pass

    def is_available(self) -> bool:
        return self._available

    def relax(self, pdb_path: str, output_path: str) -> str:
        if not self.is_available():
            raise RuntimeError("PyRosetta is not installed.")
            
        import pyrosetta
        from pyrosetta import rosetta
        
        # Initialize PyRosetta if not already
        if not pyrosetta.rosetta.basic.options.option.has_user_options():
             pyrosetta.init("-mute all") # Mute output for cleanliness
        
        # Load pose
        pose = pyrosetta.pose_from_pdb(pdb_path)
        
        # Setup FastRelax
        scorefxn = pyrosetta.get_fa_scorefxn()
        relax = rosetta.protocols.relax.FastRelax()
        relax.set_scorefxn(scorefxn)
        
        # Run relax
        print(f"[PyRosetta] Relaxing {pdb_path}...")
        relax.apply(pose)
        
        # Save
        pose.dump_pdb(output_path)
        return output_path

class MockRelaxer(RosettaRelaxer):
    """
    Mock relaxer for testing or when Rosetta is unavailable.
    Just copies the file.
    """
    def is_available(self) -> bool:
        return True

    def relax(self, pdb_path: str, output_path: str) -> str:
        print(f"[MockRelaxer] Simulating relaxation for {pdb_path}...")
        import shutil
        shutil.copy(pdb_path, output_path)
        return output_path

def get_relaxer(prefer_pyrosetta: bool = True) -> RosettaRelaxer:
    """Factory to get the best available relaxer."""
    if prefer_pyrosetta:
        relaxer = PyRosettaRelaxer()
        if relaxer.is_available():
            return relaxer
    
    return MockRelaxer()
