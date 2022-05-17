class Co2_Meter:
    def __init__(self) -> None:

        self.total_grid_consumed_house = 0
        self.total_lost_in_out = 0
        self.total_lost_in_in = 0
        self.total_grid_in_battery = 0
        self.total_produced_in_battery = 0

        self.prev_kWs_batteries = 0
    
    def reset(self):
        self.total_grid_consumed_house = 0
        self.total_lost_in_out = 0
        self.total_lost_in_in = 0
        self.total_grid_in_battery = 0
        self.total_produced_in_battery = 0
    
    def amount_co2(self, stat_batteries, ev_garage):
        
        curr_kWs_batteries = sum([battery.current_Capacity for battery in stat_batteries] + \
            [ev.battery.current_Capacity for ev in ev_garage.get_All_Vehicles()])

        amortize_batteries = curr_kWs_batteries - self.prev_kWs_batteries
        self.prev_kWs_batteries = curr_kWs_batteries


        totalenergybatteries = self.total_produced_in_battery + self.total_grid_in_battery
        percentage_gridEnergy_in_battery = totalenergybatteries / self.total_grid_in_battery
        lost_in_out_dirty = percentage_gridEnergy_in_battery * (self.total_lost_in_in + self.total_lost_in_out) 
        
        total_dirty_energy_consumed = self.total_grid_consumed_house + (self.total_grid_in_battery - amortize_batteries - lost_in_out_dirty)
        return total_dirty_energy_consumed * 0.233
        #https://bulb.co.uk/carbon-tracker/

    
    def update(self, decisions):
        
        for charge in range(0, len(decisions), 2):
            discharge = charge + 1

            if decisions[discharge].obj == "Grid":
                #total_grid_bought += decisions[discharge].energy_amount

                if decisions[charge].obj == "Consumption":
                    self.total_grid_consumed_house += decisions[charge].energy_amount
                else:
                    self.total_lost_in_in += decisions[charge].energy_amount * 0.02
                    self.total_grid_in_battery += decisions[discharge].energy_amount * 0.98
            
            elif decisions[discharge].obj == "Production":
                #total_produced += decisions[discharge].energy_amount

                if decisions[charge].obj == "Consumption":
                    #total_produced_consumed_house += decisions[charge].energy_amount
                    pass
                elif decisions[charge].obj == "Grid":
                    #produced_Not_utilized += decisions[charge].energy_amount
                    pass
                else:
                    self.total_lost_in_in += decisions[charge].energy_amount * 0.02
                    self.total_produced_in_battery += decisions[charge].energy_amount * 0.98
            
            else:   #from battery
                self.total_lost_in_out += decisions[discharge].energy_amount / 0.98  * 0.02

                if decisions[charge].obj != "Consumption":
                    self.total_lost_in_in += decisions[charge].energy_amount * 0.02
