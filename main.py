"""
Main Simulation

RUN this file
"""

from Consumption.Consumption_Prediction import Consumption_Prediction
from Consumption.Consumption_Meter import Consumption_Meter
from Consumption.Consumption_BaseLine import Consumption_BaseLine
from Consumption.Consumption_cheat import Consumption_Cheat
from EV.EV_Garage import EV_Garage
from Production.Production_Meter import Production_Meter
from datetime import datetime, timedelta
from Battery import Battery
from Decision.decisionAlg_Smart import Decision_Alg_Smart
from Decision.decisionAlg_Dumber import Decision_Alg_Dumber
from Grid import Grid_Linear, Grid_sinusoidal
from Co2_Meter import Co2_Meter
import argparse
from prettytable import PrettyTable


def execute(arg):
    """
    Executes Simulation with the given Arguments

    args:
    args.ev, type=int, default = 2, help="number of Evs"
    args.batt, type=int, default = 1, help="number of Stationary Batteries"
    args.alg, type=str, default="smart", choices=["smart", "base"], help="Decision algorithm"
    args.house, type=int, default = 0, help="Test File"
    args.pA, type=int, default = 10, help="Panel Area"
    args.pF, type=str, default="London", choices=["Portugal", "London"], help="Production file"
    args.grid, type=str, default="dynamic", choices=["flat", "dynamic"], help="Grid Price"
    args.cheat, help="Read consumption prediction in cheat file (faster)"

    Returns Iterator with reults for 12 months
    """

    #CO2 Meter will measure amount of co2 in throughout the experiment
    co2 =  Co2_Meter()


    #Initialize Consumption Meter
    consumption_Meter = Consumption_Meter(test_number = arg.house)
    current_Date = consumption_Meter.get_Start_Date()

    #Initialize CONSUMPTION PREDICTION MODULE
    featuresNames = ['use', 'hour', 'weekday']
    targetName = ['use']
    past_window = 24
    if arg.alg == "smart":
        if arg.cheat:
            consumption_Prediction = Consumption_Cheat(past_window, arg.house)
        else:
            consumption_Prediction = Consumption_Prediction(past_window, featuresNames, targetName)
    elif arg.alg == "base":
        consumption_Prediction = Consumption_BaseLine(targetName)

    #Initialize PRODUCTION
    production_meter = Production_Meter(current_Date, solar_Panel_Area=arg.pA, file=arg.pF)

    #Initialize EVS
    ev_Garage = EV_Garage(arg.ev)

    #Initialize STATIONARY BATTERY
    stationary_batteries = []
    for i in range(arg.batt):
        stationary_batteries.append(Battery())

    #Initialize GRID
    if arg.grid == "flat":
        grid = Grid_Linear()
    elif arg.grid == "dynamic":
        grid = Grid_sinusoidal()

    #Initialize Decision Algorithm
    if arg.alg == "smart":
        decision_algorithm = Decision_Alg_Smart()
    elif arg.alg == "base":
        decision_algorithm = Decision_Alg_Dumber()

    #Variables to measure results
    bill_cost = 0
    battery_cost = 0
    hour_Index = 0
    monthCounter = 0
    total_house_consumption = 0
    total_production = 0

    simul_start = 0


    """
    Main Loop
    Runs experiment for 1 year in 1 hour time steps
    """
    while True:
        simul_start += 1

        #Get consumption prediction values
        consumption_Current_Value = consumption_Meter.get_Meter_Value()
        consumption_Prediction.new_Record(consumption_Current_Value)
        consumption_Prediction_Value = consumption_Prediction.get_Prediction()

        try:
            consumption_Prediction_Value = consumption_Prediction_Value[0]
        except:
            pass
        

        #Only actually start to record results after 24 hours
        #(consumption prediction needs 24h prior info)
        if simul_start <= 24:
            continue
                
        hour_Index += 1

        #Get Real Consumption value of the next time step
        #(to Correct errors in the consumption prediction)
        consumption_Next_Value = consumption_Meter.get_Meter_Value()
        consumption_Meter.revert_Step()

        #Get Production Value
        production_Current_Value = production_meter.get_Meter_Value()

        #Get Parked EVS
        ev_Garage.next(current_Date)

        #Update Grid with current hour
        grid.update(current_Date)


        #CALL DECISION ALGORITHM WITH THE COLLECTED VARIABLES
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


        #Execute decisions made by the decision algorithm
        for decision in decisions:
            
            #Update bill cost if energy was bought from the grid
            if decision.obj == "Grid" and decision.mode == "discharge": 
                bill_cost += grid.kwh_price * decision.energy_amount

            #If house/production/grid work is done
            if isinstance(decision.obj, str): 
                continue
                
            #perform charge/discharge action  
            #update battery cost metric  
            battery_cost += decision.obj.charge(decision.energy_amount) if decision.mode == "charge" \
                else decision.obj.discharge(decision.energy_amount)

        #UPDATE METRICS
        co2.update(decisions, consumption_Next_Value["use"])
        total_house_consumption += consumption_Current_Value["use"]
        total_production += production_Current_Value
        current_Date = current_Date + timedelta(hours=1)

        #REPORT monthly results
        if hour_Index == 30*24:
            emited_co2 = co2.amount_co2(stationary_batteries, ev_Garage)
            yield bill_cost, battery_cost, ev_Garage.empaired_evs, total_house_consumption, total_production, emited_co2 


            #RESET metrics for the next month
            hour_Index = 0
            ev_Garage.empaired_evs = 0
            bill_cost = 0
            battery_cost = 0
            total_production = 0
            total_house_consumption = 0
            co2.reset()
            monthCounter += 1
            
            #END experiment in 1 year
            if monthCounter == 12:
                return


if __name__ == "__main__":

    #READ ARGUMENTS
    parser = argparse.ArgumentParser()
    parser.add_argument("-ev", type=int, default = 2, help="number of Evs")
    parser.add_argument("-batt", type=int, default = 1, help="number of Stationary Batteries")
    parser.add_argument("-alg", type=str, default="smart", choices=["smart", "base"], help="Decision algorithm")
    parser.add_argument("-house", type=int, default = 0, help="Test File")
    parser.add_argument("-pA", type=int, default = 10, help="Panel Area")
    parser.add_argument("-pF", type=str, default="London", choices=["Portugal", "London"], help="Production file")
    parser.add_argument("-grid", type=str, default="dynamic", choices=["flat", "dynamic"], help="Grid Price")
    parser.add_argument('--cheat', action='store_true')
    args = parser.parse_args()
    
    #Prepare simulation
    simulation = execute(args)

    #table output
    t = PrettyTable(['Run', 'Total Cost', 'Bill Cost', 'Battery Cost', 'Impaired', "CO2",'House Consumption', 'Production'])

    month=0
    results = []

    #Iterate over monthly simulation results
    #Gather results in a pretty table
    for month_results in simulation:
        month+=1

        bill_cost, battery_cost, impaired, house_consumption, production, co2 = month_results

        result = [month, round(bill_cost + battery_cost,2), \
                        round(bill_cost ,2), \
                        round(battery_cost,2), \
                        impaired, \
                        round(co2,2), \
                        round(house_consumption,2), \
                        round(production,2)]

        t.add_row(result)
        results.append(result)

    t.add_row(["Total", round(sum([r[1] for r in results]),2), \
                        round(sum([r[2] for r in results]) ,2), \
                        round(sum([r[3] for r in results]),2), \
                        sum([r[4] for r in results]), \
                        round(sum([r[5] for r in results]),2), \
                        round(sum([r[6] for r in results]),2), \
                        round(sum([r[7] for r in results]),2)])

    print(t)




