from EV.EV import EV
import random
import numpy as np
from datetime import timedelta

class EV_Garage:
    def __init__(self, max_Evs) -> None:
        self.max_Evs = max_Evs
        self.current_Evs = []
        self.commonArrivalHours = [12, 13, 17, 18, 21, 22]
        self.evArrival_Prob = 0.1 
    
    def get_Current_Vehicles(self):
        return [ev["ev"] for ev in self.current_Evs]

    #consoante hora probabilidade de ec sair / chegar, mesmo ev nao tem q seguir um padrao
    def next(self, current_Date):
        #Evs leaving
        for ev_info in list(self.current_Evs):
            ev_info["dep_Time"] -= 1        
        self.current_Evs = [ev_info for ev_info in self.current_Evs if ev_info["dep_Time"] > 0]

        #Evs arriving
        if len(self.current_Evs) < self.max_Evs:
            p = self.evArrival_Prob
            if current_Date.hour in self.commonArrivalHours:
                p += 0.15
        
            if random.random() < p: #CAR ARRIVED
                departure_Time = round(np.random.triangular(1, 3, 24, size=None))
                
                sigma = departure_Time/4 #quanto mais pequeno departure mais certeza

                departure_guess = round(random.gauss(departure_Time, sigma))
                departure_guess = 1 if departure_guess < 1 else departure_guess

                charge_needed = round(random.gauss(40, 10))
                if charge_needed < 15:
                    charge_needed = 15
                elif charge_needed > 100:
                    charge_needed = 100

                soc = round(np.random.triangular(1, 3, 100, size=None))
                
                ev = EV(soc/100, batterry_Threshold=charge_needed/100)
                ev.departure_Time = current_Date + timedelta(hours=departure_guess)

                ev_info = {"dep_Time":departure_Time, "ev": ev}
                self.current_Evs.append(ev_info)

                #print("EV ARRIVED: " + str(ev_info)) 

        return self.current_Evs