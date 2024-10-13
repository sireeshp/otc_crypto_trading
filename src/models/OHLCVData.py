from dataclasses import dataclasses

@dataclasses
class OHLCVData:
    timestamp:int
    open:float
    high:float
    low:float
    close:float
    volume:float