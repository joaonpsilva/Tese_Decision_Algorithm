"""
EV_GARAGE CLASS

Keeps track of all the EVs in the simulation and respective state
Emulates travel patterns
"""

from EV.EV import EV
import random
import numpy as np
from datetime import timedelta, datetime


class EV_Garage:
    def __init__(self, max_Evs) -> None:

        #Number of Evs in the simulation
        self.max_Evs = max_Evs
        
        #EVs that are currently parked at home and able to dis/charge
        self.parked_Evs = []

        #EVs that are away and not available
        self.away_Evs = [EV() for i in range(max_Evs)]

        #hour to boost arrival chance
        self.commonArrivalHours = [11,12,13,18,19,20,22,23]

        #hour to boost departure chance
        self.leave_hours = [8, 14, 20]
        self.evArrival_Prob = 0.1

        self.empaired_evs = 0
    
    def get_Current_Vehicles(self):
        """
        GET parked vehicles
        return array of EVs
        """
        return [ev["ev"] for ev in self.parked_Evs]
    
    def get_All_Vehicles(self):
        """
        GET all vehicles
        return array of EVs
        """
        return [ev["ev"] for ev in self.parked_Evs] + self.away_Evs

    
    def evs_leaving(self):
        """
        Check if is time for EV to depart

        Each parked EV contains a counter of hours till departure.
        This function is run every hour and decreases that counter.
        When counter hits 0, EV leaves
        """

        for ev_info in list(self.parked_Evs):

            #ev_info keeps counter of hours till departure
            ev_info["dep_Time"] -= 1   
            if ev_info["dep_Time"] == 0:    
                
                #Check if EV has a satisfied threshold
                if ev_info["ev"].battery.soc < ev_info["ev"].batterry_Threshold:
                    self.empaired_evs += 1
                
                #EV leaves
                self.away_Evs.append(ev_info["ev"])

        self.parked_Evs = [ev_info for ev_info in self.parked_Evs if ev_info["dep_Time"] > 0]
    


    def evs_arriving(self, current_Date):
        """
        Make some EVs arrive.
        define all user defined parameters (threshold, departure time guess)
        define real departure time
        """

        #garage is full
        if len(self.parked_Evs) == self.max_Evs:
            return

        available_slots = self.max_Evs - len(self.parked_Evs)
        for i in range(available_slots):

            p = self.evArrival_Prob

            #boost probability in some hours
            if current_Date.hour in self.commonArrivalHours:
                p += 0.15
            
            
            if random.random() < p: 
                #CAR ARRIVED

                #get random vehicle that was away
                ev = random.choice(self.away_Evs)
                self.away_Evs.remove(ev)
                
                #SOC
                #Soc EV left with - previous threshold * used
                ev.battery.soc = ev.battery.soc - (ev.batterry_Threshold * random.uniform(0.2, 0.8)) 


                
                #BATTERY THRESHOLD
                ev.batterry_Threshold = round(np.random.triangular(0.1, 0.3, 0.8, size=None),2) #new battery threshold
                
                #minimum hours needed to charge from 0 to threshold
                needed = ev.batterry_ThresholdKWH
                needed_hours = int(needed/ev.battery.charge_Rate + 1) if needed > 0 else 0



                #REAL DEPARTURE TIME
                
                choosen_hour = random.choice(self.leave_hours) #choose hour
                choosen_hour = round(random.gauss(choosen_hour, 2)) #intruduce randomness
                #0<hour<24
                choosen_hour = 0 if choosen_hour < 0 else choosen_hour
                choosen_hour = choosen_hour - 24 if choosen_hour > 23 else choosen_hour

                #transform to datetime
                choosen_date = current_Date
                choosen_date = choosen_date.replace(hour=choosen_hour)
                #make it next day if choosen hour is less than current hour
                if choosen_date <= current_Date:
                    choosen_date += timedelta(days=1)

                #make sure it has time to charge (needed_hours variable)
                if choosen_date <= current_Date + timedelta(hours=needed_hours):
                    choosen_date += timedelta(hours=needed_hours) - (choosen_date - current_Date)



                #DEPARTURE GUESS
                #Time to departure in hours
                time_left = choosen_date - current_Date 
                time_left = int(time_left.total_seconds() / 3600)

                #Randomness
                sigma = min([time_left/4 ,1.5]) #quanto mais pequeno departure mais certeza
                departure_guess = round(random.gauss(time_left, sigma))
                departure_guess = 1 if departure_guess < 1 else departure_guess

                #set departure guess in EV
                ev.departure_Time = current_Date + timedelta(hours=departure_guess)


                #Store info                            
                ev_info = {"dep_Time":time_left, "ev": ev}
                self.parked_Evs.append(ev_info)



    def next(self, current_Date):
        """
        UPDATE simulation (called by main)

        current_Date: Datetime object

        returns array with parked Evs
        """
        
        #make EVs leave
        self.evs_leaving()

        #make EVs arrive
        self.evs_arriving(current_Date)

        return self.parked_Evs




#--------------IGNORE---------
if __name__ == "__main__":

    current_Date = datetime.now()

    ev_Garage = EV_Garage(1)

    while True:
        print("\n", current_Date)
        ev_Garage.next(current_Date)

        for ev in ev_Garage.get_Current_Vehicles():
            ev.battery.soc = max([ev.battery.soc, ev.batterry_Threshold])

        current_Date = current_Date + timedelta(hours=1)
