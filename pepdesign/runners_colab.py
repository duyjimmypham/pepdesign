"""
Runner for Google Colab environment.
Executes commands in Colab's shell with proper GPU access.
"""
import subprocess
import os
from typing import List, Optional
from pepdesign.runners import BaseRunner


class ColabRunner(BaseRunner):
    """
    Runner for Google Colab environment.
    Executes commands directly in Colab's shell.
    """
    
    def __init__(self, cwd: Optional[str] = None):
        """
        Initialize Colab runner.
        
        Args:
            cwd: Working directory for commands
        """
        self.cwd = cwd or os.getcwd()
        self._check_colab()
    
    def _check_colab(self):
        """Check if running in Google Colab."""
        try:
            import google.colab
            self._is_colab = True
        except ImportError:
            self._is_colab = False
    
    def is_available(self) -> bool:
        """Check if Colab environment is available."""
        return self._is_colab
    
    def run(self, command: List[str], cwd: Optional[str] = None, **kwargs) -> subprocess.CompletedProcess:
        """
        Run command in Colab environment.
        
        Args:
            command: Command to run as list of strings
            cwd: Working directory (overrides instance cwd)
            **kwargs: Additional arguments for subprocess
            
        Returns:
            CompletedProcess object
        """
        if not self.is_available():
            raise RuntimeError("Not running in Google Colab environment")
        
        work_dir = cwd or self.cwd
        cmd_str = " ".join(command)
        
        print(f"[ColabRunner] Running: {cmd_str}")
        print(f"[ColabRunner] Working directory: {work_dir}")
        
        # Run command
        result = subprocess.run(
            command,
            cwd=work_dir,
            capture_output=True,
            text=True,
            **kwargs
        )
        
        if result.returncode != 0:
            print(f"[ColabRunner] Error: {result.stderr}")
        
        return result
