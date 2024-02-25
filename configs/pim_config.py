from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Configuration:
    name: str
    workload: Path
    frequency: str = "3GHz"

@dataclass(frozen=True)
class Statistics:
    ticks: int
