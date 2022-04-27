from EV import EV
import random
import numpy as np

class EV_Garage:
    def __init__(self, max_Evs) -> None:
        self.max_Evs = max_Evs
        self.current_Evs = []
        self.commonArrivalHours = [12, 13, 17, 18, 21, 22]
        self.evArrival_Prob = 0.1 

    #consoante hora probabilidade de ec sair / chegar, mesmo ev nao tem q seguir um padrao
    def next(self):
        #Evs leaving
        for ev_info in self.current_Evs:
            ev_info["dep_Time"] -= 1
            if ev_info["dep_Time"] == 0:
                print("EV LEFT" + str(ev_info["ev"]))
                self.current_Evs.remove(ev_info)

        #Evs arriving
        if len(self.current_Evs) < self.maxEvs:
            p = self.evArrival_Prob
            if self.current_Date.hour in self.commonArrivalHours:
                p += 0.15
        
            if random.random() < p: #CAR ARRIVED
                departure_Time = round(np.random.triangular(1, 3, 24, size=None))
                
                sigma = departure_Time/4 #quanto mais pequeno departure mais certeza

                departure_guess = round(random.gauss(departure_Time, sigma))
                departure_guess = 1 if departure_guess < 1 else departure_guess

                charge_needed = random.gauss(40, 10)
                if charge_needed < 15:
                    charge_needed = 15
                elif charge_needed > 100:
                    charge_needed = 100

                soc = round(np.random.triangular(1, 3, 100, size=None))
                
                ev = EV(soc, batterry_Threshold=charge_needed)
                ev.departure_Time(departure_guess)

                ev_info = {"dep_Time":departure_Time, "ev": ev}
                self.current_Evs.append(ev_info)

                print("EV ARRIVED: " + str(ev_info)) 

        return self.current_Evs