from dataclasses import dataclass


@dataclass
class OHLCVData:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
