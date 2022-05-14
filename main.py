from Consumption.Consumption_Prediction import Consumption_Prediction
from Consumption.Consumption_Meter import Consumption_Meter
from Consumption.Consumption_BaseLine import Consumption_BaseLine
from EV.EV_Garage import EV_Garage
from Production.Production_Prediction import Production_Meter
from datetime import datetime, timedelta
from Battery import Battery
from Decision.decisionAlg import Decision_Alg
from Decision.decisionAlg_Dumber import Decision_Alg_Dumber
from Grid import Grid_Linear, Grid_sinusoidal
import argparse
from prettytable import PrettyTable


def execute(alg, ev_number, t, p, grid, prod_file):
    consumption_Meter = Consumption_Meter(test_number = t)
    current_Date = consumption_Meter.get_Start_Date()

    #CONSUMPTION PREDICTION MODULE
    featuresNames = ['use', 'hour', 'weekday']
    targetName = ['use']
    past_window = 24
    if alg == "smart":
        consumption_Prediction = Consumption_Prediction(past_window, featuresNames, targetName)
    elif alg == "dumb":
        consumption_Prediction = Consumption_BaseLine(targetName)

    #PRODUCTION
    production_meter = Production_Meter(current_Date, solar_Panel_Area=p, file=prod_file)

    #EVS
    ev_Garage = EV_Garage(ev_number)

    #BATTERY
    stationary_battery = Battery(battery_size = 50)

    #GRID
    if grid == "flat":
        grid = Grid_Linear()
    elif grid == "dynamic":
        grid = Grid_sinusoidal()

    #Decision
    if alg == "smart":
        decision_algorithm = Decision_Alg()
    elif alg == "dumb":
        decision_algorithm = Decision_Alg_Dumber()

    bill_cost = 0
    battery_cost = 0
    i = 0
    monthCounter = 0
    total_house_consumption = 0
    total_production = 0

    simul_start = 0
    while True:
        simul_start += 1

        #CONSUMPTION PREDICTION
        consumption_Current_Value = consumption_Meter.get_Meter_Value()
        consumption_Prediction.new_Record(consumption_Current_Value)
        consumption_Prediction_Value = consumption_Prediction.get_Prediction()
        try:
            consumption_Prediction_Value = consumption_Prediction_Value[0]
        except:
            pass

        if simul_start <= 24:
            continue
        
        i += 1

        #REAL VALUE
        consumption_Next_Value = consumption_Meter.get_Meter_Value()
        consumption_Meter.revert_Step()

        #Production
        production_Current_Value = production_meter.get_Meter_Value()

        #Evs
        ev_Garage.next(current_Date)

        #Grid
        grid.update(current_Date)


        total_house_consumption += consumption_Current_Value["use"]
        total_production += production_Current_Value


        #CALL DECISION ALG
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

            if decision.obj == "Grid" and decision.mode == "discharge": #got energy from grid
                bill_cost += grid.kwh_price * decision.energy_amount

            if isinstance(decision.obj, str):   #is not battery or ev
                continue
            
            #charged battery or ev
            if decision.mode == "charge":
                try:
                    batt = decision.obj.battery    
                except :
                    batt = decision.obj
                battery_cost += batt.kwh_price * decision.energy_amount

                
            #charge or discharge action    
            decision.obj.charge(decision.energy_amount) if decision.mode == "charge" else decision.obj.discharge(decision.energy_amount)


        current_Date = current_Date + timedelta(hours=1)

        #Report month results
        if i == 30*24:

            yield bill_cost, battery_cost, ev_Garage.empaired_evs, total_house_consumption, total_production
            i = 0
            ev_Garage.empaired_evs = 0
            bill_cost = 0
            battery_cost = 0
            total_production = 0
            total_house_consumption = 0
            monthCounter += 1

            if monthCounter == 12:
                return




parser = argparse.ArgumentParser()
parser.add_argument("-ev", type=int, default = 3, help="number of Evs")
parser.add_argument("-alg", type=str, default="smart", choices=["smart", "dumb"], help="Decision algorithm")
parser.add_argument("-t", type=int, default = 0, help="Test File")
parser.add_argument("-panel", type=int, default = 9, help="Panel Area")
parser.add_argument("-pf", type=str, default="Portugal", choices=["Portugal", "London"], help="Production file")
parser.add_argument("-grid", type=str, default="flat", choices=["flat", "dynamic"], help="Grid Price")

args = parser.parse_args()

t = PrettyTable(['Run', 'Total Cost', 'Bill Cost', 'Battery Cost', 'Impaired', 'House Consumption', 'Production'])
total_bill_cost, total_battery_cost, total_impaired, total_house_consumption, total_production = 0,0,0,0,0

simulation = execute(args.alg, args.ev, args.t, args.panel, args.grid, args.pf)

i=0 
for month_results in simulation:
    i+=1
    bill_cost, battery_cost, impaired, house_consumption, production = month_results

    t.add_row([i, bill_cost+battery_cost, bill_cost,battery_cost, impaired, house_consumption, production])

    total_bill_cost += bill_cost
    total_battery_cost += battery_cost
    total_impaired += impaired
    total_house_consumption += house_consumption
    total_production += production

t.add_row(["mean", total_bill_cost/i + total_battery_cost/i, \
        total_bill_cost / i, total_battery_cost/i, total_impaired / i,\
            total_house_consumption/i, total_production/i])
print(t)