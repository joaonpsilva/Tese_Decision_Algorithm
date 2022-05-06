from Consumption.Consumption_Prediction import Consumption_Prediction
from Consumption.Consumption_Meter import Consumption_Meter
from EV.EV_Garage import EV_Garage
from Production.Production_Prediction import Production_Meter
from datetime import datetime, timedelta
from Battery import Battery
from Decision.decisionAlg import Decision_Alg
from Decision.decisionAlg_Dumber import Decision_Alg_Dumber
from Grid import Grid_Linear, Grid_sinusoidal
import argparse
from prettytable import PrettyTable


def execute(alg, ev_number, t, p):
    consumption_Meter = Consumption_Meter(test_number = t)
    current_Date = consumption_Meter.get_Start_Date()

    #CONSUMPTION PREDICTION MODULE
    featuresNames = ['use', 'hour', 'weekday']
    targetName = ['use']
    past_window = 24
    consumption_Prediction = Consumption_Prediction(past_window, featuresNames, targetName)

    #PRODUCTION
    production_meter = Production_Meter(current_Date, solar_Panel_Area=p)

    #EVS
    ev_Garage = EV_Garage(ev_number)

    #BATTERY
    stationary_battery = Battery(battery_size = 50)

    #GRID
    grid = Grid_sinusoidal()

    #Decision
    if alg == "smart":
        decision_algorithm = Decision_Alg()
    elif alg == "dumb":
        decision_algorithm = Decision_Alg_Dumber()

    total_cost = 0
    i = 0

    while True:

        #CONSUMPTION PREDICTION
        consumption_Current_Value = consumption_Meter.get_Meter_Value()
        consumption_Prediction.new_Record(consumption_Current_Value)
        consumption_Prediction_Value = consumption_Prediction.get_Prediction()
        try:
            consumption_Prediction_Value = consumption_Prediction_Value[0]
        except:
            pass

        if consumption_Prediction_Value is None:
            continue
        
        #REAL VALUE
        consumption_Next_Value = consumption_Meter.get_Meter_Value()
        consumption_Meter.revert_Step()

        #Production
        production_Current_Value = production_meter.get_Meter_Value()

        #Evs
        ev_Garage.next(current_Date)

        #Grid
        grid.update(current_Date)

        #print("\n------------------Date: ", current_Date, "----------------------------------------")
        #print("Consumption Prediction: ", consumption_Prediction_Value)
        #print("Consumption Real value: ", consumption_Next_Value["use"])
        #print("Production Value: ", production_Current_Value)
        #print("Connected Vehicles ", ev_Garage.get_Current_Vehicles())
        #print("Stationary Battery ", stationary_battery)


        context = {
                "consumption_prediction": consumption_Prediction_Value,
                "production": production_Current_Value,
                "connected_EVs":ev_Garage.get_Current_Vehicles(),
                "current_Time":current_Date,
                "stationary_Batteries": [stationary_battery],
                "grid": grid,
                "Real_consumption": consumption_Next_Value["use"]
            }


        decisions = decision_algorithm.analyse(context)

        for decision in decisions:
            #print("\n-----------DECISIONS-----------\n")
            #print(decision)

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
    print("EMPAIRED EVS: ", ev_Garage.empaired_evs)

    return total_cost, ev_Garage.empaired_evs


parser = argparse.ArgumentParser()
parser.add_argument("-ev", type=int, default = 3, help="number of Evs")
parser.add_argument("-alg", type=str, default="smart", choices=["smart", "dumb"], help="Decision algorithm")
parser.add_argument("-t", type=int, default = 0, help="Test File")
parser.add_argument("-p", type=int, default = 9, help="Panel Area")
args = parser.parse_args()

t = PrettyTable(['Run', 'Cost', 'Impaired'])

total_cost, total_impaired = 0,0
for i in range(10):
    cost, impaired = execute(args.alg, args.ev, args.t, args.p)

    t.add_row([i, cost, impaired])

    total_cost += cost
    total_impaired += impaired

t.add_row(["mean", total_cost / 10, total_impaired / 10])
print(t)

#python3 main.py -ev 3 -t 0 -alg dumb


# +------+--------------------+----------+
# | Run  |        Cost        | Impaired |
# +------+--------------------+----------+
# |  0   | 211.94826880818647 |    0     |
# |  1   | 212.0704086056312  |    0     |
# |  2   | 260.07905808317105 |    0     |
# |  3   | 257.86480352587324 |    1     |
# |  4   | 253.85036663410173 |    0     |
# |  5   | 230.39519466474874 |    0     |
# |  6   | 259.3303719645566  |    0     |
# |  7   | 209.94104390608166 |    0     |
# |  8   | 240.74757311583528 |    1     |
# |  9   | 255.64928474276547 |    0     |
# | mean | 239.18763740509513 |   0.2    |
# +------+--------------------+----------+

# +------+--------------------+----------+
# | Run  |        Cost        | Impaired |
# +------+--------------------+----------+
# |  0   | 163.48339964989773 |    1     |
# |  1   | 158.50410416081803 |    3     |
# |  2   | 195.86075019261614 |    0     |
# |  3   | 148.6611736637193  |    1     |
# |  4   | 210.16801703296295 |    4     |
# |  5   | 149.84577587043705 |    2     |
# |  6   | 160.76798317976107 |    7     |
# |  7   | 182.35786711976485 |    2     |
# |  8   | 174.6018105760738  |    3     |
# |  9   | 189.1019852140284  |    3     |
# | mean | 173.33528666600796 |   2.6    |
# +------+--------------------+----------+
#27.5 %





    