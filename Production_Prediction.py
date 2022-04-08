
class Production_Prediction:

    def __init__(self, solar_Panel_Area):
        
        self._solar_Panel_Area = solar_Panel_Area

    
    @property
    def solar_Panel_Area(self):
        return self._solar_Panel_Area

    @solar_Panel_Area.setter
    def solar_Panel_Area(self, value):
        self._solar_Panel_Area = value

    def make_Prediction(self):
        return 0