import math

class Grid_Linear:
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
    def __init__(self, hour = 0) -> None:
        self.hour = hour
    
    def update(self, date):
        self.hour = date.hour

    @property
    def kwh_price(self):
        return 0.15 * (math.cos( (self.hour/4) - 10.5) + 1) + 0.1
    
    @property
    def average_kwh_price(self):
        return 0.25