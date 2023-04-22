import pandas
import os
from re import sub

dirs=["0","1","2","3","4","5","6","7","8","9"]
subdirs = ["Scenario1", "Scenario2", "Scenario3"]

algs = {"smart":0, "base":0}

i=0
for d in dirs:
    for s in subdirs:
        directory = d + "/" + s + "/"
        for f in os.listdir(directory):
            if f[-3:] == "csv":

                i+=1
                if f[:4] == "base":
                    alg = "base"
                else:
                    alg = "smart"


                csv_file = directory + f

                file = open(csv_file)
                csvreader = pandas.read_csv(file)

                algs[alg] += csvreader["CO2"].iloc[-1]

algs["smart"] = algs["smart"] / (i/2)
algs["base"] = algs["base"] / (i/2)

print("Smart", algs["smart"])
print("Base", algs["base"])







