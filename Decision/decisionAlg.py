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
            expected_error = 2
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
            batteries_total = sum([b.current_Capacity for b in context["stationary_Batteries"]])
            if batteries_total < -expected_remaining:#battery does not contain a lot of energy
                
                #check if evs can deal with lack of energy
                total_dispending = sum([ev.battery.current_Capacity - ev.batterry_ThresholdKWH\
                                        for ev in context["connected_EVs"] \
                                            if ev not in needing_charge and \
                                                ev.departure_Time - context["current_Time"] >= timedelta(hours=4)])
                            
                if total_dispending < -expected_remaining:
                    
                    #battery with more free space
                    choosen_battery = sorted([b for b in context["stationary_Batteries"] ], key = lambda x: x.battery_size - x.current_Capacity)[-1]
                    energy_needed = (-expected_remaining) - choosen_battery.current_Capacity
                    free_battery_space = choosen_battery.battery_size - choosen_battery.current_Capacity

                    #charge rate is max that can charge in 1H
                    e = min([energy_needed, choosen_battery.charge_Rate,free_battery_space] )
                    
                    #1.5 priority -> evs leaving soon
                    self.receive_Priority.append(Priority_Object(choosen_battery, 1.5, e))
        
        
        #STATIONARY BATTERY
        for battery in context["stationary_Batteries"]:
            free_battery_space = battery.battery_size - battery.current_Capacity
            e = min([battery.charge_Rate,free_battery_space] )
            self.receive_Priority.append(Priority_Object(battery, 1, e))

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
        total_free_space = sum([battery.battery_size - battery.current_Capacity for battery in context["stationary_Batteries"]])

        choosen_battery = None
        if expected_remaining is not None and expected_remaining > 0 and total_free_space < expected_remaining: #house will produce more energy
            choosen_battery = sorted([b for b in context["stationary_Batteries"] ], key = lambda x: x.current_Capacity)[-1]
            free_space = choosen_battery.battery_size - choosen_battery.current_Capacity
            energy_dispending = expected_remaining - free_space
            choosen_e = min([choosen_battery.charge_Rate, energy_dispending] )
            self.give_Priority.append(Priority_Object(choosen_battery, 1, choosen_e))
        
        for battery in context["stationary_Batteries"]:
            if battery.kwh_price < context["grid"].kwh_price: #charging battery costs less than grid
                e = min([battery.charge_Rate, battery.current_Capacity] )
                if choosen_battery is not None and choosen_battery == battery:  #already gave choosen_e with 1 priority cannot give again
                    e = min([battery.charge_Rate, battery.current_Capacity - choosen_e] )

                self.give_Priority.append(Priority_Object(battery, 2, e))

        #GRID
        #if grid really low price fill everything?
        if context["grid"].kwh_price <= 0.005:
            grid_P = 1
        elif min([b.kwh_price for b in context["stationary_Batteries"]]) > context["grid"].kwh_price or context["grid"].kwh_price <= 0.5 * context["grid"].average_kwh_price:
            grid_P = 1.5
        else:
            grid_P = 3
        self.give_Priority.append(Priority_Object("Grid", grid_P, 99999999))

        self.give_Priority.sort(key=lambda x: x.priority)



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


