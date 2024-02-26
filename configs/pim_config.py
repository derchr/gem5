from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Configuration:
    name: str
    workload: str
    executable: Path
    pim: bool
    level: str
    frequency: str = "3GHz"

@dataclass(frozen=True)
class Statistics:
    ticks: int
