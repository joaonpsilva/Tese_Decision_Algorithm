from EV import EV
from Stationary_Battery import Stationary_Battery
from Consumption.Consumption_Prediction import Consumption_Prediction
from Production.Production_Prediction import Production_Meter
from datetime import timedelta
from Decision import Decision
from Priority_Object import Priority_Object

class Decision_Alg:
    
    def __init__(self):

        self.connected_EVs = []

        self.receive_Priority = []
        self.give_Priority = []
    
    def analyse(self, context):


        expected_error = 1
        expected_remaining =  context.pruction - (context.consumption + expected_error)

        self.define_receive_Priority(context.current_Time,
                                       expected_remaining,
                                       context.stationary_Battery)

        self.define_give_Priority(expected_remaining,
                                       context.stationary_Battery)
        
        self.make_Deciosions()

    
    def define_receive_Priority(self, current_Time, expected_remaining, stationary_Battery):

        #ENERGY CONSUMPTION    
        self.receive_Priority.append(Priority_Object("Consumption", 0, -1))

        #EVS WITH LOW BATTERY
        needing_charge = [ev for ev in self.connected_EVS if ev.soc < ev.batterry_Threshold]
        needing_charge.sort(key=lambda x: x.departure_Time)
        for ev in needing_charge:
            charge_needed = ev.batterry_Threshold - ev.soc
            time_diff = ev.departure_Time - current_Time
            time2charge = charge_needed / ev.charge_Rate

            if time2charge - time_diff < timedelta(hours=2):
                self.receive_Priority.append(Priority_Object(ev, 0, charge_needed))
            else:
                self.receive_Priority.append(Priority_Object(ev, 1, charge_needed))

        #STATIONARY BATTERY
        if expected_remaining < 0 and stationary_Battery.current_Capacity < -expected_remaining: #house will need energy
            energy_needed = expected_remaining - stationary_Battery.current_Capacity
            self.receive_Priority.append(Priority_Object(stationary_Battery, 1, energy_needed))
        
        self.receive_Priority.append(Priority_Object(stationary_Battery, 2, -1))

        #OTHER EVS
        for ev in self.connected_EVs:
            if ev not in needing_charge:
                self.receive_Priority.append(Priority_Object(ev, 2, -1))
    
    def define_give_Priority(self, expected_remaining, stationary_Battery):

        #PRODUCTION
        self.give_Priority.append(Priority_Object("Production", 0, -1))
        
        #EVS with more charge
        dispending_charge = [ev for ev in self.connected_EVS if ev.soc > ev.batterry_Threshold]
        dispending_charge.sort(key=lambda x: x.soc - x.batterry_Threshold)
        for ev in dispending_charge:
            charge_dispendable = ev.soc - ev.batterry_Threshold
            self.give_Priority.append(Priority_Object(ev, 1, charge_dispendable))
        
        #STATIONARY BATTERY
        free_space_battery = stationary_Battery.max_Capacity - stationary_Battery.current_Capacity
        if expected_remaining > 0 and free_space_battery < expected_remaining: #house will need energy
            energy_dispending = expected_remaining - free_space_battery
            self.receive_Priority.append(Priority_Object(stationary_Battery, 1, energy_dispending))
        
        self.receive_Priority.append(Priority_Object(stationary_Battery, 2, -1))

        #GRID
        self.give_Priority.append(Priority_Object("Grid", 3, -1))

    
    def make_Decisions(self):


        decisions = []
        self.give_Priority = [obj for obj in self.give_Priority if obj.amount_kw > 0]

        for obj_receive in self.receive_Priority:


            if obj_receive.priority != 0:
                give_Priority_0_kw = sum([x.amount_kw for x in self.give_Priority if x.priority == 0])
                
                #object is not priority and no availabe
                if give_Priority_0_kw <= 0:
                    break
                
                priority_flag = False #only receive from priority give
                will_receive = obj_receive.amount_kw if give_Priority_0_kw >= obj_receive.amount_kw else give_Priority_0_kw
            else:
                priority_flag = True
                will_receive = obj_receive.amount_kw
                    
            decisions.append(Decision(obj_receive, "receive", will_receive))

            #Find who will give energy
            for obj_give in self.give_Priority:

                if not priority_flag and obj_give.priority != 0:
                    break
                
                obj_give.amount_kw -= will_receive
                if obj_give.amount_kw >= 0: #can give more, receiver is satisfied
                    decisions.append(Decision(obj_give, "give", will_receive))
                    break
                else:   #giver doesnt have enough, receiver is not satisfied
                    #CHECK IF CAN DO THIS
                    decisions.append(Decision(obj_give, "give", obj_give.amount_kw))
                    


#https://www.directenergyregulatedservices.com/blog/kw-vs-kwh-whats-difference


