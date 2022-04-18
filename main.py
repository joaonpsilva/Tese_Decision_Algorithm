from Consumption.Consumption_Prediction import Consumption_Prediction
from Production.Production_Prediction import Production_Meter
import os
import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

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

#EVS
maxEvs = 3
commonArrivalHours = [12, 13, 17, 18, 21, 22]
evArrival_Prob = 0.1
current_Evs = []


#consoante hora probabilidade de ec sair / chegar, mesmo ev nao tem q seguir um padrao
while True:
    print("------------------Date: ", start_Date)

    for ev in current_Evs:
        ev["dep_Time"] -= 1
        if ev["dep_Time"] == 0:
            print("EV LEFT" + str(ev))
            current_Evs.remove(ev)

    if len(current_Evs) < maxEvs:
        p = evArrival_Prob
        if start_Date.hour in commonArrivalHours:
            p += 0.15
    
        if random.random() < p: #CAR ARRIVED
            departure_Time = round(np.random.triangular(1, 3, 24, size=None))
            
            sigma = departure_Time/4 #quanto mais pequeno departure mais certeza

            departure_guess = round(random.gauss(departure_Time, sigma))
            departure_guess = 1 if departure_guess < 1 else departure_guess

            charge_needed = random.gauss(40, 10)
            if charge_needed < 15:
                charge_needed = 15
            elif charge_needed > 100:
                charge_needed = 100

            ev = {"dep_Time":departure_Time, "dep_guess": departure_guess, "charge_needed": charge_needed}
            current_Evs.append(ev)

            print("EV ARRIVED: " + str(ev))
    
    

    consumption_Prediction.new_Record(consumptionDF.iloc[index])

    print("Consumption Prediction: ", consumption_Prediction.get_Prediction())
    print("Production Value: ", production_meter.get_Meter_Value())

    start_Date = start_Date + timedelta(hours=1)
    index+=1





    