from Consumption.Consumption_Prediction import Consumption_Prediction
from Consumption.Consumption_Meter import Consumption_Meter
from EV.EV_Garage import EV_Garage
from Production.Production_Prediction import Production_Meter
from datetime import datetime, timedelta
from Stationary_Battery import Stationary_Battery
from decisionAlg import Decision_Alg

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

#BATTERY
stationary_battery = Stationary_Battery(50)

#Decision
decision_algorithm = Decision_Alg()

while True:
    print("------------------Date: ", current_Date)

    consumption_Current_Value = consumption_Meter.get_Meter_Value()
    
    consumption_Prediction.new_Record(consumption_Current_Value)
    consumption_Prediction_Value = consumption_Prediction.get_Prediction()
    try:
        consumption_Prediction_Value = consumption_Prediction_Value[0]
    except:
        pass

    production_Current_Value = production_meter.get_Meter_Value()

    ev_Garage.next(current_Date)
    print("Consumption Meter: ", consumption_Current_Value["use"])
    print("Consumption Prediction: ", consumption_Prediction_Value)
    print("Production Value: ", production_Current_Value)
    print("Connected Vehicles ", ev_Garage.get_Current_Vehicles())

    context = {
        "consumption": consumption_Prediction_Value,
        "production": production_Current_Value,
        "connected_EVs":ev_Garage.get_Current_Vehicles(),
        "current_Time":current_Date,
        "stationary_Battery": stationary_battery,
    }

    if consumption_Prediction_Value != None:
        decisions = decision_algorithm.analyse(context)
        for d in decisions:
            print(d)
        break


    current_Date = current_Date + timedelta(hours=1)





    