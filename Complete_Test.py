from main import execute
from prettytable import PrettyTable
import matplotlib.pyplot as plt
from pathlib import Path
import copy

class Args:

    def __init__(self, name) -> None:
        
       self.ev = 2
       self.batt = 1
       self.alg= None
       self.house = 0
       self.pA = 9
       self.pF ="London"
       self.grid = "dynamic"
       self.cheat = True

       self.name = name
    
    def __repr__(self) -> str:
        if self.alg is None:
            return self.name
        return self.alg + "_" + self.name

        
    def __str__(self) -> str:
        if self.alg is None:
            return self.name
        return self.alg + "_" + self.name

def sub1(arg):
    arg.ev = 1
    arg.name += "_sub1"
    return arg

def sub2(arg):
    arg.ev = 3
    arg.name += "_sub2"
    return arg

def sub3(arg):
    arg.batt = 0
    arg.name += "_sub3"
    return arg

def sub4(arg):
    arg.grid = "flat"
    arg.name += "_sub4"
    return arg

def do(scenario):

    print(scenario)

    simulation = execute(scenario)
    t = PrettyTable(['Run', 'Total Cost', 'Bill Cost', 'Battery Cost', 'Impaired', "CO2",'House Consumption', 'Production'])
    month=0
    results = []
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

    return results





    

scenario1 = Args("Scenario1")
scenario1.pA = 10

scenario2 = Args("Scenario2")
scenario2.pA = 40

scenario3 = Args("Scenario3")
scenario3.pA = 70

scenarios = [scenario1, scenario2, scenario3]
subscenarios = [sub1, sub2, sub3, sub4]

house = 0
directory = "graphs/" + str(house) + "/"
Path(directory).mkdir(parents=True, exist_ok=True)



for scenario in scenarios:

    scenario_directory = directory + str(scenario)
    Path(scenario_directory).mkdir(parents=True, exist_ok=True)
    
    #SCENARIO PLOT
    plt.figure(figsize=(25,10))
    plt.title(scenario)
    plt.ylabel('Total Cost €')
    plt.xlabel('month')

    for alg, color in zip(["smart", "base"], ["-", "-."]):

        scenario_alg = copy.copy(scenario)
        scenario_alg.alg = alg

        results = do(scenario_alg)
    
        plt.plot([r[1] for r in results], linewidth=8, color = "black", linestyle=color, label=str(scenario))
        
        subMarker = ["o", "s", "X", "p"]
        subStyle = ["red", "orange", "green", "blue"]

        for subscenario, plotstyle, plotmarker in zip(subscenarios, subStyle, subMarker):
            scen = copy.copy(scenario_alg)
            scen = subscenario(scen)
            results = do(scen)

            plt.plot([r[1] for r in results], linewidth=4, linestyle=color, color=plotstyle, label=str(scen))

    plt.legend()
    plt.savefig(scenario_directory + "/" + str(scenario) + ".png")



