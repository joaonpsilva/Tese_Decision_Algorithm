from datetime import timedelta
from Decision.Decision import Decision
from Decision.Priority_Object import Priority_Object

class Decision_Alg:
    
    def __init__(self):
        pass
    
    def analyse(self, context):

        self.receive_Priority = []
        self.give_Priority = []

        
        if context["consumption_prediction"]:
            expected_error = 1
            expected_remaining =  context["production"] - (context["consumption_prediction"] + expected_error)
            # SIMULATION CORRECTION
            simulation_Error = context["Real_consumption"] - context["consumption_prediction"]
        else:
            expected_remaining = None
            simulation_Error = context["Real_consumption"]


        self.define_receive_Priority(context, expected_remaining)
        self.define_give_Priority(context, expected_remaining)


        if context["consumption_prediction"] is None or simulation_Error > 0:    #consumption was actually bigger than expected
            self.receive_Priority.append(Priority_Object("Consumption", 3, simulation_Error))


        decisions = self.make_Decisions()

        #Give back energy wasnt used SIMULATION CORRECTION
        if context["consumption_prediction"] is not None and simulation_Error < 0:  #consumption was smaller than expected
            decision = next((d for d in decisions if d.mode == "discharge" and not isinstance(d.obj, str)), None)
            if decision is not None:
                decision.energy_amount += simulation_Error

        return decisions

    
    def define_receive_Priority(self, context, expected_remaining):

        #ENERGY CONSUMPTION    
        if context["consumption_prediction"]:
            self.receive_Priority.append(Priority_Object("Consumption", 3, context["consumption_prediction"]))

        #EVS WITH LOW BATTERY
        needing_charge = [ev for ev in context["connected_EVs"] if ev.battery.soc < ev.batterry_Threshold]
        needing_charge.sort(key=lambda x: x.departure_Time)
        append_later = []
        for ev in needing_charge:
            charge_needed = ev.batterry_ThresholdKWH - ev.battery.current_Capacity
            time_diff = ev.departure_Time - context["current_Time"]
            
            time2charge = charge_needed / ev.battery.charge_Rate
            h = int(time2charge)
            m = time2charge - h
            time2charge = timedelta(hours=h, minutes=60*m)

            #charge rate is amx that can charge in 1H
            e = min([charge_needed, ev.battery.charge_Rate])
            if time_diff - time2charge <= timedelta(hours=5):   #Account for error
                self.receive_Priority.append(Priority_Object(ev, 3, e))
            else:
                append_later.append(Priority_Object(ev, 2, e))
        
        #Other EVS
        self.receive_Priority += append_later

        #STATIONARY BATTERY
        if expected_remaining is not None and expected_remaining < 0:#house will need energy
            if context["stationary_Battery"].current_Capacity < -expected_remaining + 3:#battery does not contain a lot of energy
                
                total_dispending = 0
                for ev in context["connected_EVs"]:   
                    if ev not in needing_charge:    #for evs dispending energy
                        time_diff = ev.departure_Time - context["current_Time"]
                       
                        #EV wont leave soon
                        if time_diff >= timedelta(hours=4):     
                            charge_dispending = ev.battery.current_Capacity - ev.batterry_ThresholdKWH
                            total_dispending += charge_dispending
                            
                if total_dispending < -expected_remaining + 3:
                    energy_needed = (-expected_remaining + 3) - context["stationary_Battery"].current_Capacity
                    free_battery_space = context["stationary_Battery"].battery_size - context["stationary_Battery"].current_Capacity

                    #charge rate is max that can charge in 1H
                    e = min([energy_needed, context["stationary_Battery"].charge_Rate,free_battery_space] )
                    
                    #1.5 priority -> evs leaving soon
                    self.receive_Priority.append(Priority_Object(context["stationary_Battery"], 1.5, e))
        
        
        #STATIONARY BATTERY
        free_battery_space = context["stationary_Battery"].battery_size - context["stationary_Battery"].current_Capacity
        e = min([context["stationary_Battery"].charge_Rate,free_battery_space] )
        self.receive_Priority.append(Priority_Object(context["stationary_Battery"], 1, e))

        #OTHER EVS
        for ev in context["connected_EVs"]:
            if ev not in needing_charge:
                free_space = ev.battery.battery_size - ev.battery.current_Capacity
                e = min([ev.battery.charge_Rate, free_space] )
                self.receive_Priority.append(Priority_Object(ev, 1, e))
        
        self.receive_Priority.append(Priority_Object("Grid", 0, 99999999))



    
    def define_give_Priority(self, context, expected_remaining):

        #PRODUCTION
        self.give_Priority.append(Priority_Object("Production", 0, context["production"]))

        
        #EVS with more charge
        dispending_charge = [ev for ev in context["connected_EVs"] if ev.battery.soc > ev.batterry_Threshold and ev.battery.kwh_price < context["grid"].kwh_price]
        dispending_charge.sort(key=lambda x: x.departure_Time)  #usar os q vao sair primeiro?
        for ev in dispending_charge:
            charge_dispendable = ev.battery.current_Capacity - ev.batterry_ThresholdKWH
            time_diff = ev.departure_Time - context["current_Time"]
            
            e = min([ev.battery.charge_Rate, charge_dispendable] )
            
            if time_diff <= timedelta(hours=4):     
                self.give_Priority.append(Priority_Object(ev, 1.5, e))
            else:
                self.give_Priority.append(Priority_Object(ev, 2, e))

        
        #STATIONARY BATTERY
        #STATIONARY BATTERY SPECIAL CASE
        free_space_battery = context["stationary_Battery"].battery_size - context["stationary_Battery"].current_Capacity
        e = 0
        if expected_remaining is not None and expected_remaining > 0 and free_space_battery < expected_remaining: #house will produce more energy
            energy_dispending = expected_remaining - free_space_battery
            e = min([context["stationary_Battery"].charge_Rate, energy_dispending] )
            self.give_Priority.append(Priority_Object(context["stationary_Battery"], 1, e))
        
        if context["stationary_Battery"].kwh_price < context["grid"].kwh_price: #charging battery costs less than grid
            e = min([context["stationary_Battery"].charge_Rate, context["stationary_Battery"].current_Capacity - e] )
            self.give_Priority.append(Priority_Object(context["stationary_Battery"], 2, e))

        #GRID
        #if grid really low price fill everything?
        if context["grid"].kwh_price <= 0.005:
            grid_P = 1
        elif context["stationary_Battery"].kwh_price > context["grid"].kwh_price or context["grid"].kwh_price <= 0.5 * context["grid"].average_kwh_price:
            grid_P = 2
        else:
            grid_P = 3
        self.give_Priority.append(Priority_Object("Grid", grid_P, 99999999))

        self.give_Priority.sort(key=lambda x: x.priority)



    def make_Decisions(self):

        self.give_Priority = [obj for obj in self.give_Priority if obj.amount_kw > 0]
        self.receive_Priority = [obj for obj in self.receive_Priority if obj.amount_kw > 0]

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


