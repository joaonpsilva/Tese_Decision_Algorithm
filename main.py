from Consumption.Consumption_Prediction import Consumption_Prediction
from Consumption.Consumption_Meter import Consumption_Meter
from Consumption.Consumption_BaseLine import Consumption_BaseLine
from Consumption.Consumption_cheat import Consumption_Cheat
from EV.EV_Garage import EV_Garage
from Production.Production_Prediction import Production_Meter
from datetime import datetime, timedelta
from Battery import Battery
from Decision.decisionAlg import Decision_Alg
from Decision.decisionAlg_Dumber import Decision_Alg_Dumber
from Grid import Grid_Linear, Grid_sinusoidal
from Co2_Meter import Co2_Meter
import argparse
from prettytable import PrettyTable

parser = argparse.ArgumentParser()
parser.add_argument("-ev", type=int, default = 3, help="number of Evs")
parser.add_argument("-batt", type=int, default = 1, help="number of Stationary Batteries")
parser.add_argument("-alg", type=str, default="smart", choices=["smart", "base"], help="Decision algorithm")
parser.add_argument("-house", type=int, default = 0, help="Test File")
parser.add_argument("-pA", type=int, default = 9, help="Panel Area")
parser.add_argument("-pF", type=str, default="Portugal", choices=["Portugal", "London"], help="Production file")
parser.add_argument("-grid", type=str, default="flat", choices=["flat", "dynamic"], help="Grid Price")
parser.add_argument('--cheat', action='store_true')
args = parser.parse_args()



def execute():

    co2 =  Co2_Meter()

    consumption_Meter = Consumption_Meter(test_number = args.house)
    current_Date = consumption_Meter.get_Start_Date()

    #CONSUMPTION PREDICTION MODULE
    featuresNames = ['use', 'hour', 'weekday']
    targetName = ['use']
    past_window = 24
    if args.alg == "smart":
        if args.cheat:
            consumption_Prediction = Consumption_Cheat(past_window, args.house)
        else:
            consumption_Prediction = Consumption_Prediction(past_window, featuresNames, targetName)
    elif args.alg == "base":
        consumption_Prediction = Consumption_BaseLine(targetName)

    #PRODUCTION
    production_meter = Production_Meter(current_Date, solar_Panel_Area=args.pA, file=args.pF)

    #EVS
    ev_Garage = EV_Garage(args.ev)

    #BATTERY
    stationary_batteries = []
    for i in range(args.batt):
        stationary_batteries.append(Battery())

    #GRID
    if args.grid == "flat":
        grid = Grid_Linear()
    elif args.grid == "dynamic":
        grid = Grid_sinusoidal()

    #Decision
    if args.alg == "smart":
        decision_algorithm = Decision_Alg()
    elif args.alg == "base":
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
                "stationary_Batteries": stationary_batteries,
                "grid": grid,
                "Real_consumption": consumption_Next_Value["use"]
            }


        decisions = decision_algorithm.analyse(context)
        co2.update(decisions, consumption_Next_Value["use"])

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
            emited_co2 = co2.amount_co2(stationary_batteries, ev_Garage)
            yield bill_cost, battery_cost, ev_Garage.empaired_evs, total_house_consumption, total_production, emited_co2 

            i = 0
            ev_Garage.empaired_evs = 0
            bill_cost = 0
            battery_cost = 0
            total_production = 0
            total_house_consumption = 0
            co2.reset()
            monthCounter += 1

            if monthCounter == 12:
                return



t = PrettyTable(['Run', 'Total Cost', 'Bill Cost', 'Battery Cost', 'Impaired', "CO2",'House Consumption', 'Production'])
total_bill_cost, total_battery_cost, total_impaired, total_house_consumption, total_production, total_co2 = 0,0,0,0,0,0

simulation = execute()

month=0
for month_results in simulation:
    month+=1

    bill_cost, battery_cost, impaired, house_consumption, production, co2 = month_results


    t.add_row([month, round(bill_cost + battery_cost,2), \
                    round(bill_cost ,2), \
                    round(battery_cost,2), \
                    impaired, \
                    round(co2,2), \
                    round(house_consumption,2), \
                    round(production,2)])

    total_bill_cost += bill_cost
    total_battery_cost += battery_cost
    total_impaired += impaired
    total_house_consumption += house_consumption
    total_production += production
    total_co2 += co2

t.add_row(["Total", round(total_bill_cost + total_battery_cost,2), \
                    round(total_bill_cost ,2), \
                    round(total_battery_cost,2), \
                    total_impaired, \
                    round(total_co2,2), \
                    round(total_house_consumption,2), \
                    round(total_production,2)])

print(t)