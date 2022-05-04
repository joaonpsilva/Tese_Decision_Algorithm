from Consumption.Consumption_Prediction import Consumption_Prediction
from Consumption.Consumption_Meter import Consumption_Meter
from EV.EV_Garage import EV_Garage
from Production.Production_Prediction import Production_Meter
from datetime import datetime, timedelta
from Battery import Battery
from decisionAlg import Decision_Alg
from decisionAlg_Dummer import Decision_Alg_Dummer
from Grid import Grid_Linear

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
stationary_battery = Battery(battery_size = 50)

#GRID
grid = Grid_Linear()

#Decision
decision_algorithm = Decision_Alg()

total_cost = 0
i = 0

while True:

    consumption_Current_Value = consumption_Meter.get_Meter_Value()
    consumption_Next_Value = consumption_Meter.get_Meter_Value()
    consumption_Meter.revert_Step()

    consumption_Prediction.new_Record(consumption_Current_Value)
    consumption_Prediction_Value = consumption_Prediction.get_Prediction()
    try:
        consumption_Prediction_Value = consumption_Prediction_Value[0]
    except:
        pass

    production_Current_Value = production_meter.get_Meter_Value()

    ev_Garage.next(current_Date)
    
    
    if consumption_Prediction_Value != None:
        print("\n------------------Date: ", current_Date, "----------------------------------------")
        print("Consumption Prediction: ", consumption_Prediction_Value)
        print("Consumption Real value: ", consumption_Next_Value["use"])
        print("Production Value: ", production_Current_Value)
        print("Connected Vehicles ", ev_Garage.get_Current_Vehicles())
        print("Stationary Battery ", stationary_battery)


        context = {
                "consumption_prediction": consumption_Prediction_Value,
                "production": production_Current_Value,
                "connected_EVs":ev_Garage.get_Current_Vehicles(),
                "current_Time":current_Date,
                "stationary_Battery": stationary_battery,
                "grid": grid,
                "Real_consumption": consumption_Next_Value["use"]
            }

        print("\n-----------DECISIONS-----------\n")

        decisions = decision_algorithm.analyse(context)

        for decision in decisions:
            print(decision)

            if decision.obj == "Grid" and decision.mode == "discharge":
                total_cost += grid.kwh_price * decision.energy_amount

            if isinstance(decision.obj, str):
                continue
            
            decision.obj.charge(decision.energy_amount) if decision.mode == "charge" else decision.obj.discharge(decision.energy_amount)


    current_Date = current_Date + timedelta(hours=1)
    i += 1
    if i == 30*24:
        break

print("TOTAL COST: ", total_cost)





    