from Consumption_Prediction import Consumption_Prediction
from Production_Prediction import Production_Prediction
from Stationary_Battery import Stationary_Battery

class House:

    def __init__(self):
        
        self.production_Model = Production_Prediction()
        self.consumption_Model = Consumption_Prediction()
    