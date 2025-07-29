from dataclasses import dataclass
from typing import Optional


@dataclass
class SleepData:
    """Data model for baby sleep information"""
    naps: int
    longestSleep: float
    totalSleep: float
    daySleep: float
    nightSleep: float
    nightWakings: int

    @staticmethod
    def from_dict(data: dict) -> 'SleepData':
        """
        Create a SleepData instance from a dictionary
        
        Args:
            data: Dictionary containing sleep data
            
        Returns:
            SleepData: New instance with data from dictionary
        """
        return SleepData(
            naps=data.get('naps', 0),
            longestSleep=round(data.get('longestSleep', 0) / 60, 1),
            totalSleep=round(data.get('totalSleep', 0) / 60, 1),
            daySleep=round(data.get('daySleep', 0) / 60, 1),
            nightSleep=round(data.get('nightSleep', 0) / 60, 1),
            nightWakings=data.get('nightWakings', 0)
        ) 