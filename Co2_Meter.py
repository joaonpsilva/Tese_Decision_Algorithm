"""
Co2 METER

This class keeps track of how much Co2
is being emmited in the experient (roughly) every month
"""


class Co2_Meter:
    def __init__(self) -> None:

        #energe consumed by the household, provided by the grid
        self.total_grid_consumed_house = 0

        #energy lost in battery discharging actions
        self.total_lost_in_out = 0

        #energy lost in battery charging actions
        self.total_lost_in_in = 0

        #energy lost/sold to the grid from batteries
        self.total_lost_to_Grid = 0

        #energy stored in batteries that was provided by the grid
        self.total_grid_in_battery = 0

        #energy stored in batteries that was provided by the solar panels
        self.total_produced_in_battery = 0

        #energy that was stored in the batteries at the last time the meter was run
        self.prev_kWs_batteries = 0
    
    def reset(self):
        """
        Reset metrics
        """
        self.total_grid_consumed_house = 0
        self.total_lost_in_out = 0
        self.total_lost_in_in = 0
        self.total_grid_in_battery = 0
        self.total_produced_in_battery = 0
        self.total_lost_to_Grid = 0
    
    def amount_co2(self, stat_batteries, ev_garage):
        """
        Calculate kG of emited co2
        
        stat_batteries: array with stationary batteries
        ev_garage: obj that will return array with EVs

        returns KG os Co2

        """
        
        #get total energy stored in batteries and find the % grid source
        totalenergy_batteries = self.total_produced_in_battery + self.total_grid_in_battery
        
        percentage_gridEnergy_in_battery = self.total_grid_in_battery / totalenergy_batteries \
                                                if totalenergy_batteries > 0 else 0
        
        #get current energy stored in batteries that came from grid
        #this will be deducted(as it was not consumed)
        curr_kWs_batteries = sum([battery.current_Capacity for battery in stat_batteries] + \
            [ev.battery.current_Capacity for ev in ev_garage.get_All_Vehicles()]) * percentage_gridEnergy_in_battery

        #subtract amount in batteries in the previous co2 meter run
        amortize_batteries = curr_kWs_batteries - self.prev_kWs_batteries
        self.prev_kWs_batteries = curr_kWs_batteries

        #Get energy from grid that was lost in dis/charging actions (therefore not consumed)
        lost_inout_dirty = percentage_gridEnergy_in_battery * (self.total_lost_in_in + self.total_lost_in_out)

        #total grid energy is sum:
        #-consumed by the house from the grid
        #-consumed by the house from batteries that came from grid before being in battery
        total_dirty_energy_consumed = self.total_grid_consumed_house + (self.total_grid_in_battery - \
                                                                        amortize_batteries - \
                                                                        lost_inout_dirty - \
                                                                        self.total_lost_to_Grid * percentage_gridEnergy_in_battery)
        #transform kWh to KG
        return total_dirty_energy_consumed * 0.233

    
    def update(self, decisions, real_house_consumption):
        """
        Update Metrics Every hour

        decisions: Decision Algorithm decisions
        real_house_consumption: real house consumption

        """
        
        for charge in range(0, len(decisions), 2):
            #Every charge action as a even index and every discharge action has an odd index
            discharge = charge + 1

            if decisions[discharge].obj == "Grid":  #From Grid

                if decisions[charge].obj == "Consumption":  #To House
                    consumed = min([decisions[charge].energy_amount,real_house_consumption])
                    self.total_grid_consumed_house += consumed
                else: #To Battery
                    self.total_lost_in_in += decisions[charge].energy_amount * 0.02
                    self.total_grid_in_battery += decisions[discharge].energy_amount * 0.98
            
            elif decisions[discharge].obj == "Production": #From Panels

                if decisions[charge].obj == "Consumption":  #To House
                    pass
                elif decisions[charge].obj == "Grid":   #To Grid
                    pass
                else:   #To battery
                    self.total_lost_in_in += decisions[charge].energy_amount * 0.02
                    self.total_produced_in_battery += decisions[charge].energy_amount * 0.98
            
            else:   #From battery
                self.total_lost_in_out += decisions[discharge].energy_amount / 0.98  * 0.02

                if decisions[charge].obj != "Consumption":  #To House
                    self.total_lost_in_in += decisions[charge].energy_amount * 0.02
                else: #To Grid
                    consumed = min([decisions[charge].energy_amount,real_house_consumption])
                    self.total_lost_to_Grid += decisions[charge].energy_amount - consumed

                    
