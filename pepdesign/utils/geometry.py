"""
Geometry utility functions for spatial calculations.
"""
import numpy as np
from typing import List, Tuple

def calculate_centroid(coords: List[np.ndarray]) -> Tuple[float, float, float]:
    """
    Calculate centroid of a set of coordinates.
    
    Args:
        coords: List of 3D coordinate arrays
        
    Returns:
        Centroid as (x, y, z) tuple
    """
    if not coords:
        return (0.0, 0.0, 0.0)
    
    center_arr = sum(coords) / len(coords)
    return (float(center_arr[0]), float(center_arr[1]), float(center_arr[2]))

def calculate_distance(coord1: np.ndarray, coord2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        coord1: First coordinate
        coord2: Second coordinate
        
    Returns:
        Distance
    """
    return float(np.linalg.norm(coord1 - coord2))

def place_on_circle(
    center: Tuple[float, float, float],
    radius: float,
    num_points: int,
    z_offset: float = 0.0
) -> List[Tuple[float, float, float]]:
    """
    Place points evenly on a circle in XY plane.
    
    Args:
        center: Circle center (x, y, z)
        radius: Circle radius
        num_points: Number of points to place
        z_offset: Z-axis offset from center
        
    Returns:
        List of (x, y, z) coordinates
    """
    points = []
    angle_step = 2 * np.pi / num_points
    
    for i in range(num_points):
        angle = i * angle_step
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        z = center[2] + z_offset
        points.append((float(x), float(y), float(z)))
    
    return points
