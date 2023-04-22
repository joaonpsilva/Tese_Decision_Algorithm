"""
SCRIPT TO RUN ALL SUBSCENARIOS FOR 10 DIFFERENT HOUSES 
"""

from main import execute
from prettytable import PrettyTable
import matplotlib.pyplot as plt
from pathlib import Path
import copy
import csv

class Args:

    def __init__(self, name) -> None:
        
       self.ev = 2
       self.batt = 1
       self.alg= None
       self.house = 0
       self.pA = 10
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
    #t = PrettyTable(['Run', 'Total Cost', 'Bill Cost', 'Battery Cost', 'Impaired', "CO2",'House Consumption', 'Production'])
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

        #t.add_row(result)
        results.append(result)

    results.append(["Total", round(sum([r[1] for r in results]),2), \
                        round(sum([r[2] for r in results]) ,2), \
                        round(sum([r[3] for r in results]),2), \
                        sum([r[4] for r in results]), \
                        round(sum([r[5] for r in results]),2), \
                        round(sum([r[6] for r in results]),2), \
                        round(sum([r[7] for r in results]),2)])

    #print(t)

    return results, ['Run', 'Total Cost', 'Bill Cost', 'Battery Cost', 'Impaired', "CO2",'House Consumption', 'Production']



scenario1 = Args("Scenario1")
scenario1.pA = 10

scenario2 = Args("Scenario2")
scenario2.pA = 40

scenario3 = Args("Scenario3")
scenario3.pA = 70

scenarios = [scenario1, scenario2, scenario3]
subscenarios = [sub1, sub2, sub3, sub4]

f_average = open("graphs/average/average.txt", "w")
for scenario in scenarios:

    average = [[],[],[],[],[],[],[],[],[],[]]

    for house in range(10):
        print("house: ", house)
        directory = "graphs/" + str(house) + "/"
        Path(directory).mkdir(parents=True, exist_ok=True)


        scenario.house = house
        scenario_directory = directory + str(scenario)
        Path(scenario_directory).mkdir(parents=True, exist_ok=True)
        
        #SCENARIO PLOT
        plt.figure(figsize=(25,10))
        plt.title(str(scenario) + ", House " + str(house),fontsize=20)
        plt.ylabel('Total Cost €')
        plt.xlabel('month')
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)

        for alg, style,index in zip(["smart", "base"], ["-", ":"], [0,5]):

            scenario_alg = copy.copy(scenario)
            scenario_alg.alg = alg

            #DO BASE SCENARIO
            results, header = do(scenario_alg)
            f = open(scenario_directory + "/" + str(scenario_alg) + ".csv", 'w')
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(results)
            f.close()


            average[index].append([r[1] for r in results[:-1]])
        
            plt.plot([r[1] for r in results[:-1]], linewidth=8, color = "black", linestyle=style, label=str(scenario_alg))
            
            #subMarker = ["o", "s", "X", "p"]
            subStyle = ["red", "orange", "green", "blue"]


            #ITERATE OVER SUBSCENARIOS
            for subscenario, color in zip(subscenarios, subStyle):
                index+=1
                scen = copy.copy(scenario_alg)
                scen = subscenario(scen)
                

                #DO SUBSCENARIO
                results, header = do(scen)
                f = open(scenario_directory + "/" + str(scen) + ".csv", 'w')
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(results)
                f.close()
                
                average[index].append([r[1] for r in results[:-1]])

                plt.plot([r[1] for r in results[:-1]], linewidth=4, linestyle=style, color=color, label=str(scen))

        plt.legend(fontsize=20)
        plt.savefig(scenario_directory + "/" + str(scenario) + ".png")
    

    plotStyle = [("black", 8, "-", "Smart"),
                ("red", 4, "-", "Smart_sub1"),
                ("orange", 4, "-", "Smart_sub2"),
                ("green", 4, "-", "Smart_sub3"),
                ("blue", 4, "-", "Smart_sub4"),
                ("black", 8, ":", "Base"),
                ("red", 4, ":", "Base_sub1"),
                ("orange", 4, ":", "Base_sub2"),
                ("green", 4, ":", "Base_sub3"),
                ("blue", 4, ":", "Base_sub4")]

    average_final = [[],[],[],[],[],[],[],[],[],[]]
    for sen in range(len(average)):
        for mont in range(12):
            average_final[sen].append(sum([house[mont] for house in average[sen]]) / 10)
        
        f_average.write(plotStyle[sen][3] + "  " + str(sum(average_final[sen])) + "\n")
    
    plt.figure(figsize=(25,10))
    plt.title(str(scenario) + " Average",fontsize=20)
    plt.ylabel('Total Cost €')
    plt.xlabel('month')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    
                
    for l,style in zip(average_final, plotStyle) :
        plt.plot(l, linewidth=style[1], linestyle=style[2], color=style[0], label=style[3])
    
    plt.legend(fontsize=20)
    plt.savefig(str(scenario) + ".png")

    f_average.write("\n\n")

f_average.close()





    




