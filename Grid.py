"""
GRID CLASS
Distribution Grid can supply energy
"""

import math

class Grid_Linear:
    """
    GRID with linear price per kWh
    """
    def __init__(self) -> None:
        pass

    def update(self, date):
        pass

    @property
    def kwh_price(self):
        return 0.2
    
    @property
    def average_kwh_price(self):
        return 0.2


class Grid_sinusoidal:
    """
    GRID with variable price per kWh
    """
    def __init__(self, hour = 0) -> None:
        self.hour = hour
    
    def update(self, date):
        """
        receive current hour from the simulation to update price
        """
        self.hour = date.hour

    @property
    def kwh_price(self):
        return 0.15 * (math.cos( (self.hour/3.82) - 10.5) + 1) + 0.05
    
    @property
    def average_kwh_price(self):
        return 0.2