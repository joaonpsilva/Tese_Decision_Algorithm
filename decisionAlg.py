from EV import EV
from Stationary_Battery import Stationary_Battery
from Consumption.Consumption_Prediction import Consumption_Prediction
from Production.Production_Prediction import Production_Meter
from datetime import datetime, timedelta
from Decision import Decision
from Priority_Object import Priority_Object

class Decision_Alg:
    
    def __init__(self):

        self.production_Model = Production_Meter()
        self.consumption_Model = Consumption_Prediction()
        self.stationary_Battery = Stationary_Battery()
        self.connected_EVs = []
        self.current_Time = None

        self.receive_Priority = []
        self.give_Priority = []
    
    def define_receive_Priority(self):
        
        self.receive_Priority.append(Priority_Object(Consumption, 0, 0))

        needing_charge = [ev for ev in self.connected_EVS if ev.soc < ev.batterry_Threshold]
        needing_charge.sort(key=lambda x: x.departure_Time)
        for ev in needing_charge:
            charge_needed = ev.batterry_Threshold - ev.soc
            time_diff = ev.departure_Time - self.current_Time
            time2charge = charge_needed / charge_needed

            if time2charge - time_diff < timedelta(hours=2):
                self.receive_Priority.append(Priority_Object(ev, 0, charge_needed))
            else:
                self.receive_Priority.append(Priority_Object(ev, 1, charge_needed))
        
        self.receive_Priority.append(Priority_Object(self.stationary_Battery, 2, 0))

        for ev in self.connected_EVs:
            if ev not in needing_charge:
                self.receive_Priority.append(Priority_Object(ev, 2, 0))
    
    def define_give_Priority(self):
        self.give_Priority.append(Priority_Object(Production, 0, 0))
        dispending_charge = [ev for ev in self.connected_EVS if ev.soc > ev.batterry_Threshold]
        dispending_charge.sort(key=lambda x: x.soc - x.batterry_Threshold)

        for ev in dispending_charge:
            charge_dispendable = ev.soc - ev.batterry_Threshold
            self.give_Priority.append(Priority_Object(ev, 1, charge_dispendable))
        
        self.give_Priority.append(Priority_Object(self.stationary_Battery, 2, 0))

        self.give_Priority.append(Priority_Object(Grid, 3, 0))

    
    def make_Decisions(self):

        receive_Priority_0_kw = sum([x.amount_kw for x in self.receive_Priority if x.priority == 0])
        give_Priority_0_kw = sum([x.amount_kw for x in self.give_Priority if x.priority == 0])


        
        for obj_receive in self.receive_Priority:


            if obj_receive.priority != 0:
                give_Priority_0_kw = sum([x.amount_kw for x in self.give_Priority if x.priority == 0])
                if give_Priority_0_kw > 0:
                    #GO
                    pass
            
            if obj_receive.priority == 0:
                Decision(obj_receive, "receive", obj_receive.amount_kw)

                for obj_give in self.give_Priority:
                    
                    obj_give.amount_kw -= obj_receive.amount_kw
                    if obj_give.amount_kw > 0: #can give more
                        Decision(obj_give, "give", obj_receive.amount_kw)
                        pass
                    else:
                        #CHECK IF CAN DO THIS
                        Decision(obj_give, "give", obj_give.amount_kw)
                        self.give_Priority.remove(obj_give)

                    
                    obj_receive.amount_kw -= obj_give.amount_kw
                    if obj_receive.amount_kw > 0: #need more
                        continue
                    else:
                        break
                        
                    


#https://www.directenergyregulatedservices.com/blog/kw-vs-kwh-whats-difference


    










    
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


