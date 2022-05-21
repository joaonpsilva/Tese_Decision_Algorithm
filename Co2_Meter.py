class Co2_Meter:
    def __init__(self) -> None:

        self.total_grid_consumed_house = 0
        self.total_lost_in_out = 0
        self.total_lost_in_in = 0
        self.total_lost_to_Grid = 0
        self.total_grid_in_battery = 0
        self.total_produced_in_battery = 0

        self.prev_kWs_batteries = 0
    
    def reset(self):
        self.total_grid_consumed_house = 0
        self.total_lost_in_out = 0
        self.total_lost_in_in = 0
        self.total_grid_in_battery = 0
        self.total_produced_in_battery = 0
        self.total_lost_to_Grid = 0
    
    def amount_co2(self, stat_batteries, ev_garage):
        
        
        totalenergy_batteries = self.total_produced_in_battery + self.total_grid_in_battery
        
        percentage_gridEnergy_in_battery = self.total_grid_in_battery / totalenergy_batteries \
                                                if totalenergy_batteries > 0 else 0
        

        curr_kWs_batteries = sum([battery.current_Capacity for battery in stat_batteries] + \
            [ev.battery.current_Capacity for ev in ev_garage.get_All_Vehicles()]) * percentage_gridEnergy_in_battery

        amortize_batteries = curr_kWs_batteries - self.prev_kWs_batteries
        self.prev_kWs_batteries = curr_kWs_batteries

        lost_in_out_dirty = percentage_gridEnergy_in_battery * (self.total_lost_in_in + self.total_lost_in_out)


        total_dirty_energy_consumed = self.total_grid_consumed_house + (self.total_grid_in_battery - \
                                                                        amortize_batteries - \
                                                                        lost_in_out_dirty - \
                                                                        self.total_lost_to_Grid * percentage_gridEnergy_in_battery)
        return total_dirty_energy_consumed * 0.233
        #https://bulb.co.uk/carbon-tracker/

    
    def update(self, decisions, real_house_consumption):
        
        for charge in range(0, len(decisions), 2):
            discharge = charge + 1

            if decisions[discharge].obj == "Grid":
                #total_grid_bought += decisions[discharge].energy_amount

                if decisions[charge].obj == "Consumption":
                    consumed = min([decisions[charge].energy_amount,real_house_consumption])
                    self.total_grid_consumed_house += consumed
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
                else:
                    consumed = min([decisions[charge].energy_amount,real_house_consumption])
                    self.total_lost_to_Grid += decisions[charge].energy_amount - consumed

                    
