"""
I/O utility functions for JSON and CSV operations.
"""
import json
import csv
import pandas as pd
from typing import Dict, Any, List

def load_json(json_path: str) -> Dict[str, Any]:
    """Load JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)

def save_json(data: Dict[str, Any], json_path: str, indent: int = 2) -> None:
    """Save JSON file."""
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=indent)

def load_csv(csv_path: str) -> pd.DataFrame:
    """Load CSV file as DataFrame."""
    return pd.read_csv(csv_path)

def save_csv(df: pd.DataFrame, csv_path: str, index: bool = False) -> None:
    """Save DataFrame as CSV."""
    df.to_csv(csv_path, index=index)

def load_csv_as_dicts(csv_path: str) -> List[Dict[str, Any]]:
    """Load CSV file as list of dictionaries."""
    with open(csv_path, 'r') as f:
        return list(csv.DictReader(f))

def save_csv_from_dicts(data: List[Dict[str, Any]], csv_path: str, fieldnames: List[str]) -> None:
    """Save list of dictionaries as CSV."""
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
