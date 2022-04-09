from EV import EV
from Stationary_Battery import Stationary_Battery
from Consumption_Prediction import Consumption_Prediction
from Production_Prediction import Production_Prediction
from datetime import datetime, timedelta
from Decision import Decision

class Decision_Alg:
    
    def __init__(self):

        self.production_Model = Production_Prediction()
        self.consumption_Model = Consumption_Prediction()
        self.stationary_Battery = Stationary_Battery()
        self.connected_EVs = []
        self.current_Time = None
    
    def make_Deciosions(self):

        decisions = []
            
        needing_charge = [ev for ev in self.connected_EVS if ev.soc < ev.batterry_Threshold] 
        for i in range(len(needing_charge)):
            charge_needed = needing_charge[i].batterry_Threshold - needing_charge[i].soc

            diff = needing_charge[i].departure_Time - self.current_Time
            hour_difference = diff.total_seconds() / 3600
            time2Charge = charge_needed / needing_charge[i].charge_Rate    #time in hours that ev needs to charge

            #amount of time the vehicle does not need to be charging
            canBNegleted_Time = hour_difference - time2Charge
            needing_charge[i] = (needing_charge[i], charge_needed, canBNegleted_Time)
        
        needing_charge.sort(key=lambda x : x[2]) #sort by canBNegleted_Time
        #vehicle needs to start cheging now (1 hour error)
        needing_charge_Urgent = [ev for ev in needing_charge if ev[2] < 1]
        needing_charge_Not_Urgent = needing_charge[len(needing_charge_Urgent):]


        dispending_charge = [ev for ev in self.connected_EVS if ev.soc > ev.batterry_Threshold] 
        dispending_charge.sort(key=lambda x: x.soc - x.batterry_Threshold, reverse=True)    #sort by dispendible energy (more first)


        #TAKE CARE OF needing_charge_urgent
        while len(needing_charge_Urgent) > 0:
            #MAKE DECISIONS WITH TO EV
            needing_charge_Urgent_EV, charge_needed, canBNegleted_Time = needing_charge_Urgent[0]

            if len(dispending_charge) > 0:
                dispending_charge_EV = dispending_charge[0]
                dispandable_energy = dispending_charge_EV.soc - dispending_charge_EV.batterry_Threshold

                energy_amount = charge_needed if charge_needed > dispandable_energy else dispandable_energy
                decisions.append(Decision(needing_charge_Urgent_EV, dispending_charge_EV, energy_amount))

            elif cond:
                #battery
                pass
            else:
                #rede
                pass

        
        house_Consumption =  self.consumption_Model.prediction()
        house_Production = self.production_Model.prediction()

        needing_charge if house_Consumption > house_Production else dispending_charge.append()


