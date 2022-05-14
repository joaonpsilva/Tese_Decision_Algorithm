from EV.EV import EV
import random
import numpy as np
from datetime import timedelta, datetime

class EV_Garage:
    def __init__(self, max_Evs) -> None:
        self.max_Evs = max_Evs
        
        self.parked_Evs = []
        self.away_Evs = [EV() for i in range(max_Evs)]

        self.commonArrivalHours = [12, 13, 17, 18, 21, 22]
        self.evArrival_Prob = 0.1 

        self.empaired_evs = 0
    
    def get_Current_Vehicles(self):
        return [ev["ev"] for ev in self.parked_Evs]
    
    def evs_leaving(self):
        #Evs leaving
        for ev_info in list(self.parked_Evs):
            ev_info["dep_Time"] -= 1   
            if ev_info["dep_Time"] == 0:
                #print("EV LEAVING: " + str(ev_info)) 
                if ev_info["ev"].battery.soc < ev_info["ev"].batterry_Threshold:
                    self.empaired_evs += 1
                    print("EMPAIRED", ev_info)

                self.away_Evs.append(ev_info["ev"])

        self.parked_Evs = [ev_info for ev_info in self.parked_Evs if ev_info["dep_Time"] > 0]
    


    def evs_arriving(self, current_Date):

        #garage is full
        if len(self.parked_Evs) == self.max_Evs:
            return

        available_slots = self.max_Evs - len(self.parked_Evs)
        for i in range(available_slots):

            p = self.evArrival_Prob

            #boost probability in some hours
            if current_Date.hour in self.commonArrivalHours:
                p += 0.15
        
            if random.random() < p: #CAR ARRIVED

                ev = random.choice(self.away_Evs) #get random vehicle that was away
                self.away_Evs.remove(ev)

                charged_soc = round(np.random.triangular(0, 0.2, 0.8, size=None),2) #ev might have charged
                ev.battery.soc = ev.battery.soc - (ev.batterry_Threshold * random.uniform(0.8, 0.99)) + charged_soc #previous soc - soc needed for previous trip + charged


                departure_Time = round(np.random.triangular(1, 3, 24, size=None))   #new departure time
                sigma = departure_Time/4 #quanto mais pequeno departure mais certeza
                sigma = min([sigma,1.5])
                departure_guess = round(random.gauss(departure_Time, sigma))
                departure_guess = 1 if departure_guess < 1 else departure_guess

                ev.departure_Time = current_Date + timedelta(hours=departure_guess)

                max_T = min([5/24 * departure_Time + ev.battery.soc, 0.8])
                mid = 0.15 if max_T <= 0.3 else 0.3
                    
                ev.batterry_Threshold = round(np.random.triangular(0.1, mid, max_T, size=None),2) #new battery threshold
                                
                ev_info = {"dep_Time":departure_Time, "ev": ev}
                self.parked_Evs.append(ev_info)

                #print("EV ARRIVED: " + str(ev_info)) 

    #consoante hora probabilidade de ec sair / chegar, mesmo ev nao tem q seguir um padrao
    def next(self, current_Date):
        
        self.evs_leaving()
        self.evs_arriving(current_Date)

        return self.parked_Evs

if __name__ == "__main__":

    current_Date = datetime.now()

    ev_Garage = EV_Garage(1)

    while True:
        print("\n", current_Date)
        ev_Garage.next(current_Date)

        for ev in ev_Garage.get_Current_Vehicles():
            ev.battery.soc = max([ev.battery.soc, ev.batterry_Threshold])

        current_Date = current_Date + timedelta(hours=1)
