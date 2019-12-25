from dataclasses import dataclass
from typing import List


@dataclass
class Config:
    domain: str
    target_directory: str
    base_directory: str
    modify: bool
    files: List[str]
