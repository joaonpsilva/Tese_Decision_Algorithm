from datetime import timedelta
from tokenize import triple_quoted

from pygments import highlight
from Decision.Decision import Decision
from Decision.Priority_Object import Priority_Object
from Battery import Battery

class Decision_Alg:
    
    def __init__(self):
        pass
    
    def analyse(self, context):

        self.receive_Priority = []
        self.give_Priority = []

        if context["consumption_prediction"]:
            expected_error = 2
            expected_remaining =  context["production"] - (context["consumption_prediction"] + expected_error)
        else:
            expected_remaining = None


        self.define_receive_Priority(context, expected_remaining)
        self.define_give_Priority(context, expected_remaining)
        decisions = self.make_Decisions()

        house_cons = [d.energy_amount for d in decisions if d.obj == "Consumption"]
        house_cons = house_cons[0] if len(house_cons) > 0 else 0
        simulation_Error = context["Real_consumption"] - house_cons

        if context["consumption_prediction"] is None or simulation_Error > 0:    #consumption was actually bigger than expected
            self.receive_Priority = [Priority_Object("Consumption", 3, simulation_Error)]
            self.give_Priority = [Priority_Object("Grid", 3, 999999)]
            decisions += self.make_Decisions()

        return decisions
    
    def receive_consumption(self, context):
        
        #free storage in stationary and evs
        free_storage = sum([ max([ev.battery.battery_size - ev.battery.current_Capacity, ev.battery.charge_Rate]) \
            for ev in context["connected_EVs"] ]) + \
                sum([max([battery.battery_size - battery.current_Capacity, battery.charge_Rate]) \
                    for battery in context["stationary_Batteries"]])


        #energy needed by evs
        ev_energy_need = sum([ev.batterry_ThresholdKWH - ev.battery.current_Capacity \
            for ev in context["connected_EVs"] \
                if ev.batterry_ThresholdKWH > ev.battery.current_Capacity])
        

        #energy that can be given
        ev_energy_give = sum([ev.battery.current_Capacity - ev.batterry_ThresholdKWH \
            for ev in context["connected_EVs"] \
                if ev.batterry_ThresholdKWH < ev.battery.current_Capacity])

        batery_give = sum([battery.current_Capacity for battery in context["stationary_Batteries"]])

        energy_give = ev_energy_give + batery_give + context["production"]
        energy_need = ev_energy_need

        #energy that will remaing after evs
        energy_remaining = energy_give - energy_need

        #production energy that would be trownd away
        waste = max([context["production"] - free_storage, 0])
        times_greater = energy_remaining / context["consumption_prediction"]

        if energy_remaining < 0:    #there is no energy available, will have to take from grid
            c = waste #0
        elif times_greater >= 5:    #there is plenty energy, reserve with no fear
            c = max([context["consumption_prediction"], waste])
        else:
            if context["grid"].kwh_price > context["grid"].average_kwh_price:   #there is energy and grid is expensive
                c = max([context["consumption_prediction"], waste])
            else:
                c = waste   #grid is not expensive, there is energy, reserve only waste
        
        self.receive_Priority.append(Priority_Object("Consumption", 3, c))
        


    
    def receive_EVS(self, context):
        #EVS
        context["connected_EVs"].sort(key=lambda x: x.departure_Time)
        for ev in context["connected_EVs"]:
            charge_needed = ev.batterry_ThresholdKWH - ev.battery.current_Capacity
            free_battery_space = ev.battery.battery_size - ev.battery.current_Capacity
            max_can_charge = ev.battery.charge_Rate

            if charge_needed > 0:
                time_diff = ev.departure_Time - context["current_Time"]
                time2charge = charge_needed / ev.battery.charge_Rate
                h = int(time2charge)
                m = time2charge - h
                time2charge = timedelta(hours=h, minutes=60*m)

                #charge rate is amx that can charge in 1H
                e = min([charge_needed, max_can_charge, free_battery_space])
                max_can_charge -= e
                free_battery_space -= e

                e = e / ev.battery.loss
                if time_diff - time2charge <= timedelta(hours=5):   #Account for error
                    self.receive_Priority.append(Priority_Object(ev, 3, e))
                else:
                    self.receive_Priority.append(Priority_Object(ev, 2, e))
            
            #EV may appear twice in list with different priorities
            if max_can_charge > 0 and free_battery_space > 0:
                e = min([max_can_charge, free_battery_space] )   #pick the minimum
                e = e / ev.battery.loss     
                self.receive_Priority.append(Priority_Object(ev, 1, e))
        
    
    def receive_Stationary_Batteries(self, context, expected_remaining):

        #STATIONARY BATTERY

        #compare consumption and production and find amount of energy batteries should
        #have in order to suppress possible needs the house might have
        e_should_receive = 0

        if expected_remaining is not None and expected_remaining < 0:#house will need energy
            batteries_total = sum([b.current_Capacity for b in context["stationary_Batteries"]])
                
            #check if evs can deal with lack of energy
            ev_total_dispending = sum([ev.battery.current_Capacity - ev.batterry_ThresholdKWH\
                                        for ev in context["connected_EVs"] \
                                            if ev.battery.current_Capacity - ev.batterry_ThresholdKWH > 0 and \
                                                ev.departure_Time - context["current_Time"] >= timedelta(hours=4)])
            
            e_should_receive = -expected_remaining * 2 - batteries_total + ev_total_dispending

        
        for battery in context["stationary_Batteries"]:

            free_battery_space = battery.battery_size - battery.current_Capacity
            max_can_charge = battery.charge_Rate

            if e_should_receive > 0:    #this energy has more priority

                e = min([max_can_charge, free_battery_space, e_should_receive ] )
                max_can_charge -= e
                e_should_receive -= e
                free_battery_space -= e

                e = e / battery.loss
                #1.5 priority -> evs leaving soon
                self.receive_Priority.append(Priority_Object(battery, 1.5, e))
            
            if max_can_charge > 0 and free_battery_space > 0:   #if can still charge more
                e = min([max_can_charge, free_battery_space] )
                e = e / battery.loss
                self.receive_Priority.append(Priority_Object(battery, 1, e))


    
    def define_receive_Priority(self, context, expected_remaining):

        #ENERGY CONSUMPTION    
        if context["consumption_prediction"]:
            self.receive_consumption(context)

        self.receive_EVS(context)

        self.receive_Stationary_Batteries(context, expected_remaining)
        
        self.receive_Priority.append(Priority_Object("Grid", 0, 99999999))

        self.give_Priority.sort(key=lambda x: x.priority, reverse=True)

    
    #-----------------------
    def give_Stationary_EVs(self, context):
        #EVS with more charge
        dispending_charge = [ev for ev in context["connected_EVs"] if ev.battery.soc > ev.batterry_Threshold and ev.battery.kwh_price < context["grid"].kwh_price]
        dispending_charge.sort(key=lambda x: x.departure_Time)  #usar os q vao sair primeiro?
        for ev in dispending_charge:
            charge_dispendable = ev.battery.current_Capacity - ev.batterry_ThresholdKWH
            time_diff = ev.departure_Time - context["current_Time"]
            
            e = min([ev.battery.charge_Rate, charge_dispendable] )
            e = e * ev.battery.loss
            
            if time_diff <= timedelta(hours=4):     
                self.give_Priority.append(Priority_Object(ev, 1.5, e))
            else:
                self.give_Priority.append(Priority_Object(ev, 2, e))


    def give_Stationary_Batteries(self, context, expected_remaining):
        #STATIONARY BATTERY

        if len(context["stationary_Batteries"]) == 0:
            return
        
        #if solar panels are producing to much and batteries dont have enough free space, they should
        #make room
        energy_should_give = 0
        if expected_remaining is not None and expected_remaining > 0:#house will produce more energy
            total_free_space = sum([battery.battery_size - battery.current_Capacity for battery in context["stationary_Batteries"]])

            ev_total_free_space = sum([ev.battery.battery_size - ev.battery.current_Capacity\
                                        for ev in context["connected_EVs"] \
                                            if ev.battery.current_Capacity - ev.batterry_ThresholdKWH > 0 and \
                                                ev.departure_Time - context["current_Time"] >= timedelta(hours=4)])

            energy_should_give = expected_remaining - total_free_space + ev_total_free_space
        
        for battery in context["stationary_Batteries"]:
            
            max_can_discharge = battery.charge_Rate
            capacity = battery.current_Capacity
            
            if energy_should_give > 0:  #give energy with more priority to make room

                e = min([max_can_discharge, capacity, energy_should_give] )
                max_can_discharge -= e
                energy_should_give -= e
                capacity -= e
                e = e * battery.loss
                self.give_Priority.append(Priority_Object(battery, 1, e))
            
            if capacity > 0 and max_can_discharge > 0:
                e = min([max_can_discharge, capacity] )
                e = e * battery.loss
                self.give_Priority.append(Priority_Object(battery, 2, e))


    
    def define_give_Priority(self, context, expected_remaining):

        #PRODUCTION
        self.give_Priority.append(Priority_Object("Production", 0, context["production"]))

        self.give_Stationary_EVs(context)
        
        self.give_Stationary_Batteries(context, expected_remaining)


        #GRID
        #if grid really low price fill everything?
        if context["grid"].kwh_price <= 0.005:
            grid_P = 1
        elif  context["grid"].kwh_price <= 0.5 * context["grid"].average_kwh_price or \
                (len(context["stationary_Batteries"]) > 0 and \
                    min([b.kwh_price for b in context["stationary_Batteries"]]) > context["grid"].kwh_price):
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

                if obj_receive.object == obj_give.object:
                    continue

                if isinstance(obj_receive.object, Battery) and isinstance(obj_give.object, Battery):
                    continue

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


