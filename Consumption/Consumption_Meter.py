import pandas as pd
import os
from datetime import datetime

class Consumption_Meter:
    def __init__(self, filename = None) -> None:

        if filename:
            self.consumptionDF = pd.read_csv(filename, delimiter = ',',index_col=0)
        else:
            directory = "../datsets/LCL_Data_Transformed_final/test"

            filename = sorted(os.listdir(directory))[0]
            f = os.path.join(directory, filename)
            self.consumptionDF = pd.read_csv(f, delimiter = ',',index_col=0)

        self.index=-1

        self.start_Date = self.consumptionDF.index[0]
        self.start_Date = datetime.strptime(self.start_Date[:13], '%Y-%m-%d %H')
    
    def get_Start_Date(self):
        return self.start_Date
    
    def get_Meter_Value(self):
        self.index += 1
        return self.consumptionDF.iloc[self.index]