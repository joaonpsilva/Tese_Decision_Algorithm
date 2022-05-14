from datetime import timedelta
from Decision.Decision import Decision
from Decision.Priority_Object import Priority_Object

class Decision_Alg_Dumber:
    
    
    def analyse(self, context):

        self.receive_Priority = []
        self.give_Priority = []

        self.define_receive_Priority(context)
        self.define_give_Priority(context)

        simulation_Error = context["Real_consumption"] - context["consumption_prediction"]
        if simulation_Error > 0:
            self.receive_Priority.append(Priority_Object("Consumption", 3, simulation_Error))

        decisions = self.make_Decisions()

        return decisions

    
    def define_receive_Priority(self, context):

        #ENERGY CONSUMPTION    
        self.receive_Priority.append(Priority_Object("Consumption", 3, context["consumption_prediction"]))

        #EVS
        for ev in context["connected_EVs"]:
            free_battery_space = ev.battery.battery_size - ev.battery.current_Capacity
            e = min([free_battery_space, ev.battery.charge_Rate])
            e = e / ev.battery.loss
            self.receive_Priority.append(Priority_Object(ev, 3, e))
 
        #STATIONARY BATTERY
        for battery in context["stationary_Batteries"]:
            free_battery_space = battery.battery_size - battery.current_Capacity
            e = min([battery.charge_Rate,free_battery_space] )
            e = e / battery.loss
            self.receive_Priority.append(Priority_Object(battery, 1, e))
        
        self.receive_Priority.append(Priority_Object("Grid", 0, 99999999))



    
    def define_give_Priority(self, context):

        #PRODUCTION
        self.give_Priority.append(Priority_Object("Production", 0, context["production"]))
        
        #STATIONARY BATTERY
        for battery in context["stationary_Batteries"]:
            e = min([battery.charge_Rate, battery.current_Capacity] )
            e = e / battery.loss
            self.give_Priority.append(Priority_Object(battery, 2, e))

        #GRID
        self.give_Priority.append(Priority_Object("Grid", 3, 99999999))



    def make_Decisions(self):

        self.give_Priority = [obj for obj in self.give_Priority if obj.amount_kw > 0]
        self.receive_Priority = [obj for obj in self.receive_Priority if obj.amount_kw > 0]

        decisions = []
        
        #print("RECEIVE: ", self.receive_Priority, "\n")
        #print("GIVE: ", self.give_Priority, "\n")

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


