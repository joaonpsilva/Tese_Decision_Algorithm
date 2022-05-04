from datetime import timedelta
from Decision import Decision
from Priority_Object import Priority_Object

class Decision_Alg_Dummer:
    
    def __init__(self):
        pass
    
    def analyse(self, context):

        self.receive_Priority = []
        self.give_Priority = []

        self.define_receive_Priority(context)
        self.define_give_Priority(context)

        decisions = self.make_Decisions()

        return decisions

    
    def define_receive_Priority(self, context):

        #ENERGY CONSUMPTION    
        self.receive_Priority.append(Priority_Object("Consumption", 3, context["Real_consumption"]))

        #EVS WITH LOW BATTERY
        needing_charge = [ev for ev in context["connected_EVs"] if ev.battery.soc < ev.batterry_Threshold]
        needing_charge.sort(key=lambda x: x.departure_Time)
        for ev in needing_charge:
            charge_needed = ev.batterry_ThresholdKWH - ev.battery.current_Capacity
            
            #charge rate is amx that can charge in 1H
            e = min([charge_needed, ev.battery.charge_Rate])
            self.receive_Priority.append(Priority_Object(ev, 3, e))
        
        #OTHER EVS
        for ev in context["connected_EVs"]:
            if ev not in needing_charge:
                free_space = ev.battery.battery_size - ev.battery.current_Capacity
                e = min([ev.battery.charge_Rate, free_space] )
                self.receive_Priority.append(Priority_Object(ev, 2, e))
        
        
        #STATIONARY BATTERY
        free_battery_space = context["stationary_Battery"].battery_size - context["stationary_Battery"].current_Capacity
        e = min([context["stationary_Battery"].charge_Rate,free_battery_space] )
        self.receive_Priority.append(Priority_Object(context["stationary_Battery"], 1, e))
        
        self.receive_Priority.append(Priority_Object("Grid", 0, 99999999))



    
    def define_give_Priority(self, context):

        #PRODUCTION
        self.give_Priority.append(Priority_Object("Production", 0, context["production"]))

        #if grid really low price fill everything?
        
        #STATIONARY BATTERY
        e = min([context["stationary_Battery"].charge_Rate, context["stationary_Battery"].current_Capacity] )
        self.give_Priority.append(Priority_Object(context["stationary_Battery"], 2, e))

        #GRID
        self.give_Priority.append(Priority_Object("Grid", 3, 99999999))



    def make_Decisions(self):

        decisions = []
        
        print("RECEIVE: ", self.receive_Priority)
        print()
        print("GIVE: ", self.give_Priority)
        print()


        for obj_receive in self.receive_Priority:
            
            #remove givers that were exausted in previous loop
            self.give_Priority = [obj for obj in self.give_Priority if obj.amount_kw > 0]

            for obj_give in self.give_Priority: #Find who will give energy

                if obj_give.priority <= obj_receive.priority:

                    obj_give_amount_kw_temp = obj_give.amount_kw
                    obj_give.amount_kw -= obj_receive.amount_kw

                    if obj_give.amount_kw >= 0: #can give more, receiver is satisfied
                        decisions.append(Decision(obj_receive.object, "charge", obj_receive.amount_kw))
                        decisions.append(Decision(obj_give.object, "discharge", obj_receive.amount_kw))
                        break
                    else:   #giver doesnt have enough, receiver is not satisfied
                        #CHECK IF CAN DO THIS
                        decisions.append(Decision(obj_receive.object, "charge", obj_give_amount_kw_temp))
                        decisions.append(Decision(obj_give.object, "discharge", obj_give_amount_kw_temp))
                        obj_receive.amount_kw -= obj_give_amount_kw_temp

        return decisions            


#https://www.directenergyregulatedservices.com/blog/kw-vs-kwh-whats-difference


