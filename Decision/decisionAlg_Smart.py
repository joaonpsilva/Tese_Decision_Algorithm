"""
Proposed Decision Algorithm
"""

from datetime import timedelta

from Decision.Priority_Object import Priority_Object
from Decision.Decision_Algorithm import Decision_Algorithm

class Decision_Alg_Smart(Decision_Algorithm):
    
    def __init__(self):
        super().__init__()
        self.expected_error = 2
        
    


    def receive_consumption(self, context):
        """
        Define Charge Priority and Energy Amount for the Household
        context: dictionary with simulation elements
        appends Priority Object in the priority list
        """

        if not context["consumption_prediction"]:
            return
        
        #free storage in stationary and evs
        free_storage = sum([ max([ev.battery.battery_size - ev.battery.current_Capacity, ev.battery.charge_Rate]) \
            for ev in context["connected_EVs"] ]) + \
                sum([max([battery.battery_size - battery.current_Capacity, battery.charge_Rate]) \
                    for battery in context["stationary_Batteries"]])


        #energy needed by evs
        ev_energy_need = sum([ev.batterry_ThresholdKWH - ev.battery.current_Capacity \
            for ev in context["connected_EVs"] \
                if ev.batterry_ThresholdKWH > ev.battery.current_Capacity])
        

        #energy that can be given by EVs
        ev_energy_give = sum([ev.battery.current_Capacity - ev.batterry_ThresholdKWH \
            for ev in context["connected_EVs"] \
                if ev.batterry_ThresholdKWH < ev.battery.current_Capacity])

        #energy that can be given by stationary batteries
        batery_give = sum([battery.current_Capacity for battery in context["stationary_Batteries"]])


        #energy that can be given
        energy_give = ev_energy_give + batery_give + context["production"]
        #energy that is needed
        energy_need = ev_energy_need
        #energy that will remain
        energy_remaining = energy_give - energy_need
        #times remaining is greater than consumption prediction
        times_greater = energy_remaining / context["consumption_prediction"]

        #production energy that would be trownd away
        waste = max([context["production"] - free_storage, 0])


        if energy_remaining < 0:    #there is no energy available, will have to take from grid (simul_correction)
            c = max([context["consumption_prediction"], waste]) #0
            p = 0   #only charge from solar panels

        elif times_greater >= 5:    #there is plenty energy, reserve with no fear
            c = max([context["consumption_prediction"], waste])
            p=4

        else:
            if context["grid"].kwh_price > context["grid"].average_kwh_price:   #there is energy and grid is expensive
                c = max([context["consumption_prediction"], waste])
                p=4
            else:
                c = context["consumption_prediction"] * times_greater / 5   #grid is not expensive, there is energy, reserve only waste
                self.receive_Priority.append(Priority_Object("Consumption", 4, c))
                c = max([context["consumption_prediction"], waste])
                p = 0

        self.receive_Priority.append(Priority_Object("Consumption", p, c))
        





    def receive_EVS(self, context):
        """
        Define Charge Priority and Energy Amount for EVs
        context: dictionary with simulation elements
        appends Priority Object in the priority list
        """

        context["connected_EVs"].sort(key=lambda x: x.departure_Time)
        for ev in context["connected_EVs"]:

            #kWh
            charge_needed = ev.batterry_ThresholdKWH - ev.battery.current_Capacity
            
            #kWh battery unocupied space
            free_battery_space = ev.battery.battery_size - ev.battery.current_Capacity
            
            #Ev upper bound for charging in 1 time step
            max_can_charge = ev.battery.charge_Rate

            #Needs energy
            if charge_needed > 0:

                #time left for Ev to leave
                time_diff = ev.departure_Time - context["current_Time"]
                time2charge = charge_needed / ev.battery.charge_Rate
                h = int(time2charge)
                m = time2charge - h

                #time needed to charge
                time2charge = timedelta(hours=h, minutes=60*m)

                #charge the minimum off
                e = min([charge_needed, max_can_charge, free_battery_space])
                max_can_charge -= e
                free_battery_space -= e

                #account for battery loss
                e = e / ev.battery.loss

                #if Ev will leave soon assign higher priority
                if time_diff - time2charge <= timedelta(hours=5):   #Account for error
                    self.receive_Priority.append(Priority_Object(ev, 4, e))
                else:
                    self.receive_Priority.append(Priority_Object(ev, 3, e))
            
            #EV may appear twice in list with different priorities
            #After threshold is done, EV can still charge more
            if max_can_charge > 0 and free_battery_space > 0:
                e = min([max_can_charge, free_battery_space] )   #pick the minimum
                e = e / ev.battery.loss     
                self.receive_Priority.append(Priority_Object(ev, 1, e))
        
    



    def receive_Stationary_Batteries(self, context):
        """
        Define Charge Priority and Energy Amount for the Stationary Battery
        context: dictionary with simulation elements
        appends Priority Object in the priority list
        """

        if len(context["stationary_Batteries"]) == 0:
            return

        #expected to remain from solar panels
        expected_remaining =  context["production"] - (context["consumption_prediction"] + self.expected_error)\
            if context["consumption_prediction"] is not None else None


        #compare consumption and production and find amount of energy batteries should
        #have in order to suppress possible needs the house might have
        e_should_receive = 0
        if expected_remaining is not None and expected_remaining < 0:   #house will need energy
            batteries_total = sum([b.current_Capacity for b in context["stationary_Batteries"]])    #total kWh in batteries
                
            #Total kWh in Evs that can be discharged
            ev_total_dispending = sum([ev.battery.current_Capacity - ev.batterry_ThresholdKWH\
                                        for ev in context["connected_EVs"] \
                                            if ev.battery.current_Capacity - ev.batterry_ThresholdKWH > 0 and \
                                                ev.departure_Time - context["current_Time"] >= timedelta(hours=4)])
            
            #check if battery should receive energy or there is enough
            #*2 to account for error
            e_should_receive = -expected_remaining * 2 - batteries_total + ev_total_dispending

        
        for battery in context["stationary_Batteries"]:

            free_battery_space = battery.battery_size - battery.current_Capacity
            max_can_charge = battery.charge_Rate

            #if battery should receive energy due to high consumption
            if e_should_receive > 0:    
                
                #choose minimum of charge rate, free space
                e = min([max_can_charge, free_battery_space, e_should_receive ] )
                max_can_charge -= e
                e_should_receive -= e
                free_battery_space -= e

                e = e / battery.loss
                #this energy has more priority
                self.receive_Priority.append(Priority_Object(battery, 2, e))
            
            #Battery can receive energy with normal priority till is full
            if max_can_charge > 0 and free_battery_space > 0:   #if can still charge more
                e = min([max_can_charge, free_battery_space] )
                e = e / battery.loss
                self.receive_Priority.append(Priority_Object(battery, 1, e))




    def receive_Grid(self,context):
        """
        Define Charge Priority and Energy Amount for the Grid
        context: dictionary with simulation elements
        appends Priority Object in the priority list
        """
        self.receive_Priority.append(Priority_Object("Grid", 0, 99999999))

    
    #------------------------------




    def give_EVs(self, context):
        """
        Define Disharge Priority and Energy Amount for EV
        context: dictionary with simulation elements
        appends Priority Object in the priority list
        """

        #Evs that have more energy than needed
        dispending_charge = [ev for ev in context["connected_EVs"] if ev.battery.soc > ev.batterry_Threshold and ev.battery.kwh_price < context["grid"].kwh_price]
        dispending_charge.sort(key=lambda x: x.departure_Time)  #usar os q vao sair primeiro?
        
        for ev in dispending_charge:
            
            #kWh dispendable energy
            charge_dispendable = ev.battery.current_Capacity - ev.batterry_ThresholdKWH
            
            #Time till departure
            time_diff = ev.departure_Time - context["current_Time"]
            
            #pay attention to charge rate
            e = min([ev.battery.charge_Rate, charge_dispendable] )
            e = e * ev.battery.loss
            
            #if ev leaves soon has more priority do discharge
            if time_diff <= timedelta(hours=4):     
                self.give_Priority.append(Priority_Object(ev, 2, e))
            else:
                self.give_Priority.append(Priority_Object(ev, 3, e))






    def give_Stationary_Batteries(self, context):
        """
        Define Disharge Priority and Energy Amount for Stationary Battery
        context: dictionary with simulation elements
        appends Priority Object in the priority list
        """

        if len(context["stationary_Batteries"]) == 0:
            return
        
        #expected to remain from solar panels
        expected_remaining =  context["production"] - (context["consumption_prediction"] + self.expected_error)\
            if context["consumption_prediction"] is not None else None

        #if solar panels are producing to much and batteries dont have enough free space, they should
        #make room
        energy_should_give = 0
        if expected_remaining is not None and expected_remaining > 0:#house will produce more energy

            #free space in stat batteries
            total_free_space = sum([battery.battery_size - battery.current_Capacity for battery in context["stationary_Batteries"]])

            #free space in Evs
            ev_total_free_space = sum([ev.battery.battery_size - ev.battery.current_Capacity\
                                        for ev in context["connected_EVs"] \
                                            if ev.battery.current_Capacity - ev.batterry_ThresholdKWH > 0 and \
                                                ev.departure_Time - context["current_Time"] >= timedelta(hours=4)])

            #amount of energy that shoud discharge to make space
            energy_should_give = expected_remaining - total_free_space + ev_total_free_space
        


        for battery in context["stationary_Batteries"]:
            
            max_can_discharge = battery.charge_Rate
            capacity = battery.current_Capacity
            
            if energy_should_give > 0:  #give energy with more priority to make room
                
                #attention to charge rate
                e = min([max_can_discharge, capacity, energy_should_give] )
                max_can_discharge -= e
                energy_should_give -= e
                capacity -= e
                e = e * battery.loss
                self.give_Priority.append(Priority_Object(battery, 1, e))
            
            #battery can still discharge with normal priority
            if capacity > 0 and max_can_discharge > 0:
                e = min([max_can_discharge, capacity] )
                e = e * battery.loss
                self.give_Priority.append(Priority_Object(battery, 3, e))



    
    def give_Production(self,context):
        """
        Define Disharge Priority and Energy Amount for Solar Panels
        context: dictionary with simulation elements
        appends Priority Object in the priority list
        """
        self.give_Priority.append(Priority_Object("Production", 0, context["production"]))




    
    def give_Grid(self,context):
        """
        Define Disharge Priority and Energy Amount for Grid
        context: dictionary with simulation elements
        appends Priority Object in the priority list
        """

        #if grid really low price fill everything?
        if context["grid"].kwh_price <= 0.005:
            grid_P = 1

        #grid less than average or less than price to discharge battery
        elif  context["grid"].kwh_price <= 0.5 * context["grid"].average_kwh_price or \
                (len(context["stationary_Batteries"]) > 0 and \
                    min([b.kwh_price for b in context["stationary_Batteries"]]) > context["grid"].kwh_price):
            grid_P = 2

        #grid expensive
        else:
            grid_P = 4

            
        self.give_Priority.append(Priority_Object("Grid", grid_P, 99999999))