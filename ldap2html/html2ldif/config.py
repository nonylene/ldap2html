from dataclasses import dataclass
from typing import List


@dataclass
class Config:
    domain: str
    directory: str
    modify: bool
    files: List[str]
