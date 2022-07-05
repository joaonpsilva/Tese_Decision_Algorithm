"""
Base Line Decision Algorithm
"""

from datetime import timedelta
from Decision.Decision import Decision
from Decision.Priority_Object import Priority_Object
from Decision.Decision_Algorithm import Decision_Algorithm

class Decision_Alg_Dumber(Decision_Algorithm):

    
    def receive_consumption(self,context):
        self.receive_Priority.append(Priority_Object("Consumption", 3, context["consumption_prediction"]))

    def receive_EVS(self,context):
        """
        Allways charge EVs till max capacity
        """
        for ev in context["connected_EVs"]:
            free_battery_space = ev.battery.battery_size - ev.battery.current_Capacity
            e = min([free_battery_space, ev.battery.charge_Rate])
            e = e / ev.battery.loss
            self.receive_Priority.append(Priority_Object(ev, 4, e))


    def receive_Stationary_Batteries(self,context):
        for battery in context["stationary_Batteries"]:
            free_battery_space = battery.battery_size - battery.current_Capacity
            e = min([battery.charge_Rate,free_battery_space] )
            e = e / battery.loss
            self.receive_Priority.append(Priority_Object(battery, 1, e))


    def receive_Grid(self,context):
        self.receive_Priority.append(Priority_Object("Grid", 0, 99999999))


    def give_Production(self,context):
        self.give_Priority.append(Priority_Object("Production", 0, context["production"]))


    def give_EVs(self,context):
        """
        EVs dont help household
        """
        pass


    def give_Stationary_Batteries(self,context):
        for battery in context["stationary_Batteries"]:
            e = min([battery.charge_Rate, battery.current_Capacity] )
            e = e * battery.loss
            self.give_Priority.append(Priority_Object(battery, 3, e))


    def give_Grid(self,context):
        self.give_Priority.append(Priority_Object("Grid", 4, 99999999))



