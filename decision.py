from EV import EV
from Stationary_Battery import Stationary_Battery
from Consumption_Prediction import Consumption_Prediction
from Production_Prediction import Production_Prediction

class Decision_Alg():
    
    def __init__(self):

        self.production_Model = Production_Prediction()
        self.consumption_Model = Consumption_Prediction()
        self.stationary_Battery = Stationary_Battery()
        self.connected_EVs = []