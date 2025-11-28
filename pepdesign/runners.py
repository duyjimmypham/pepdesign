"""
Runner abstraction for executing external tools.
Handles the difference between running in Docker, Local Subprocess, or Colab.
"""
from abc import ABC, abstractmethod
import subprocess
import os
import shlex
from typing import List, Dict, Optional, Union

class BaseRunner(ABC):
    """Abstract base class for tool execution."""
    
    @abstractmethod
    def run(self, command: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        """
        Execute a command.
        
        Args:
            command: List of command parts (e.g., ["python", "script.py"])
            cwd: Working directory
            env: Environment variables
            
        Returns:
            CompletedProcess object
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the runner environment is operational."""
        pass

class LocalRunner(BaseRunner):
    """Runs commands directly on the host system."""
    
    def run(self, command: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        # Security: In a real app, we'd validate 'command' more strictly.
        print(f"[LocalRunner] Executing: {' '.join(command)}")
        return subprocess.run(command, cwd=cwd, env=env, check=True, capture_output=True, text=True)

    def is_available(self) -> bool:
        return True

class DockerRunner(BaseRunner):
    """
    Runs commands inside a Docker container.
    Automatically mounts volumes.
    """
    def __init__(self, image: str, mounts: Optional[Dict[str, str]] = None):
        """
        Args:
            image: Docker image name
            mounts: Dictionary of {host_path: container_path} to mount
        """
        self.image = image
        self.mounts = mounts or {}

    def run(self, command: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        docker_cmd = ["docker", "run", "--rm"]
        
        # Add mounts
        for host_path, container_path in self.mounts.items():
            abs_host = os.path.abspath(host_path)
            docker_cmd.extend(["-v", f"{abs_host}:{container_path}"])
        
        # Set working directory inside container
        if cwd:
            docker_cmd.extend(["-w", cwd])
            
        # Add environment variables
        if env:
            for k, v in env.items():
                docker_cmd.extend(["-e", f"{k}={v}"])
                
        docker_cmd.append(self.image)
        docker_cmd.extend(command)
        
        print(f"[DockerRunner] Executing: {' '.join(docker_cmd)}")
        return subprocess.run(docker_cmd, check=True, capture_output=True, text=True)

    def is_available(self) -> bool:
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

class MockRunner(BaseRunner):
    """
    Simulates execution for testing or when tools are missing.
    """
    def run(self, command: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        print(f"[MockRunner] Simulated: {' '.join(command)}")
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="Mock Success", stderr="")

    def is_available(self) -> bool:
        return True
