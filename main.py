from Consumption.Consumption_Prediction import Consumption_Prediction
from Production.Production_Prediction import Production_Meter
import os
import pandas as pd
from datetime import datetime


directory = "../datsets/LCL_Data_Transformed/test"
filename = sorted(os.listdir(directory))[0]
f = os.path.join(directory, filename)
consumptionDF = pd.read_csv(f, delimiter = ',',index_col=0)
start_Date = consumptionDF.index[0]
start_Date = datetime.strptime(start_Date[:13], '%Y-%m-%d %H')
index=0


#CONSUMPTION PREDICTION MODULE
featuresNames = ['use', 'hour', 'weekday']
targetName = ['use']
past_window = 24
consumption_Prediction = Consumption_Prediction(past_window, featuresNames, targetName)

#PRODUCTION
production_meter = Production_Meter(start_Date)



while True:
    consumption_Prediction.new_Record(consumptionDF.iloc[index])
    index+=1


    print("Consumption Prediction: ", consumption_Prediction.get_Prediction())
    print("Production Value: ", production_meter.get_Meter_Value())


    