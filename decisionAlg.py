from datetime import timedelta
from Decision import Decision
from Priority_Object import Priority_Object

class Decision_Alg:
    
    def __init__(self):


        self.receive_Priority = []
        self.give_Priority = []
    
    def analyse(self, context):

        expected_error = 1
        expected_remaining =  context["production"] - (context["consumption"] + expected_error)

        self.define_receive_Priority(context, expected_remaining)
        self.define_give_Priority(context, expected_remaining)
        
        decisions = self.make_Decisions()

        return decisions

    
    def define_receive_Priority(self, context, expected_remaining):

        #ENERGY CONSUMPTION    
        self.receive_Priority.append(Priority_Object("Consumption", 3, context["consumption"]))

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

            if time_diff - time2charge < timedelta(hours=2):
                self.receive_Priority.append(Priority_Object(ev, 3, charge_needed))
            else:
                append_later.append(Priority_Object(ev, 2, charge_needed))
        
        #Other EVS
        self.receive_Priority += append_later

        #STATIONARY BATTERY
        if expected_remaining < 0:#house will need energy
            if context["stationary_Battery"].current_Capacity < -expected_remaining * 2:#battery does not contain a lot of energy
                
                total_dispending = 0
                vehicles_leaving_soon = 0
                for ev in context["connected_EVs"]:   
                    if ev not in needing_charge:    #for evs dispending energy
                        time_diff = ev.departure_Time - context["current_Time"]
                       
                        #EV wont leave soon
                        if time_diff >= timedelta(hours=2):     
                            charge_dispending = ev.battery.current_Capacity - ev.batterry_ThresholdKWH
                            total_dispending += charge_dispending
                        else:
                            vehicles_leaving_soon += 1
                            
                if total_dispending < -expected_remaining and vehicles_leaving_soon > 0:
                    energy_needed = (-expected_remaining * 2) - context["stationary_Battery"].current_Capacity
                    free_battery_space = context["stationary_Battery"].battery_size - context["stationary_Battery"].current_Capacity
                    e = energy_needed if energy_needed < free_battery_space else free_battery_space
                    
                    #1.5 priority -> evs leaving soon
                    self.receive_Priority.append(Priority_Object(context["stationary_Battery"], 1.5, e))
        
        
        #STATIONARY BATTERY
        free_battery_space = context["stationary_Battery"].battery_size - context["stationary_Battery"].current_Capacity
        self.receive_Priority.append(Priority_Object(context["stationary_Battery"], 1, free_battery_space))

        #OTHER EVS
        for ev in context["connected_EVs"]:
            if ev not in needing_charge:
                free_space = ev.battery.battery_size - ev.battery.current_Capacity
                self.receive_Priority.append(Priority_Object(ev, 1, free_space))
        
        self.receive_Priority.append(Priority_Object("Grid", 0, 99999999))



    
    def define_give_Priority(self, context, expected_remaining):

        #PRODUCTION
        self.give_Priority.append(Priority_Object("Production", 0, context["production"]))

        #if grid really low price fill everything?

        #STATIONARY BATTERY SPECIAL CASE
        free_space_battery = context["stationary_Battery"].battery_size - context["stationary_Battery"].current_Capacity
        if expected_remaining > 0 and free_space_battery < expected_remaining: #house will produce more energy
            energy_dispending = expected_remaining - free_space_battery
            self.give_Priority.append(Priority_Object(context["stationary_Battery"], 1, energy_dispending))
        
        #EVS with more charge
        dispending_charge = [ev for ev in context["connected_EVs"] if ev.battery.soc > ev.batterry_Threshold and ev.battery.kwh_price < context["grid"].kwh_price]

        dispending_charge.sort(key=lambda x: x.departure_Time)  #usar os q vao sair primeiro?
        for ev in dispending_charge:
            charge_dispendable = ev.battery.current_Capacity - ev.batterry_ThresholdKWH
            time_diff = ev.departure_Time - context["current_Time"]
            
            if time_diff >= timedelta(hours=1):     
                self.give_Priority.append(Priority_Object(ev, 1.5, charge_dispendable))
            else:
                self.give_Priority.append(Priority_Object(ev, 2, charge_dispendable))
        
        #STATIONARY BATTERY
        grid_P = 2
        if context["stationary_Battery"].kwh_price < context["grid"].kwh_price:
            self.give_Priority.append(Priority_Object(context["stationary_Battery"], 2, context["stationary_Battery"].current_Capacity))
            grid_P = 3

        #GRID
        self.give_Priority.append(Priority_Object("Grid", grid_P, 99999999))



    def make_Decisions(self):

        decisions = []
        
        print("RECEIVE: ", self.receive_Priority)
        print()
        print("GIVE: ", self.give_Priority)

        for obj_receive in self.receive_Priority:
            
            #remove givers that were exausted in previous loop
            self.give_Priority = [obj for obj in self.give_Priority if obj.amount_kw > 0]

            for obj_give in self.give_Priority: #Find who will give energy

                if obj_give.priority <= obj_receive.priority:

                    obj_give_amount_kw_temp = obj_give.amount_kw
                    obj_give.amount_kw -= obj_receive.amount_kw

                    if obj_give.amount_kw >= 0: #can give more, receiver is satisfied
                        decisions.append(Decision(obj_receive.object, "receive", obj_receive.amount_kw))
                        decisions.append(Decision(obj_give.object, "give", obj_receive.amount_kw))
                        break
                    else:   #giver doesnt have enough, receiver is not satisfied
                        #CHECK IF CAN DO THIS
                        decisions.append(Decision(obj_receive.object, "receive", obj_give_amount_kw_temp))
                        decisions.append(Decision(obj_give.object, "give", obj_give_amount_kw_temp))
                        obj_receive.amount_kw -= obj_give_amount_kw_temp

        return decisions            


#https://www.directenergyregulatedservices.com/blog/kw-vs-kwh-whats-difference


