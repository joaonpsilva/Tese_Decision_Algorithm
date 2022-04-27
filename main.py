from Consumption.Consumption_Prediction import Consumption_Prediction
from Consumption.Consumption_Meter import Consumption_Meter
from EV import EV_Garage
from Production.Production_Prediction import Production_Meter
import os
import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

consumption_Meter = Consumption_Meter()
current_Date = consumption_Meter.get_Start_Date()

#CONSUMPTION PREDICTION MODULE
featuresNames = ['use', 'hour', 'weekday']
targetName = ['use']
past_window = 24
consumption_Prediction = Consumption_Prediction(past_window, featuresNames, targetName)

#PRODUCTION
production_meter = Production_Meter(current_Date)

#EVS
ev_Garage = EV_Garage(3)


while True:
    print("------------------Date: ", current_Date)

    current_Consumption = consumption_Meter.get_Meter_Value()
    consumption_Prediction.new_Record(current_Consumption)

    print("Consumption Prediction: ", consumption_Prediction.get_Prediction())
    print("Production Value: ", production_meter.get_Meter_Value())

    ev_Garage.next()

    current_Date = current_Date + timedelta(hours=1)





    