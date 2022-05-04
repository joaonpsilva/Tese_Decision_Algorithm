class Battery:

    def __init__(self, soc = 0, battery_size = 50, charge_Rate = 5, battery_price = 10000, cycles = 5000):
        
        #https://thenextweb.com/news/ev-battery-basics-kw-kwh-electric-vehicle-charging-lingo
        self._charge_Rate = charge_Rate
        self._battery_size = battery_size
        self._current_Capacity = battery_size * soc

        self.battery_price = battery_price
        self.cycles = cycles

        self.calc_costToCharge()

    
    def calc_costToCharge(self):
        self.price_per_kWh = self.battery_price / (self.cycles * self.battery_size) 
    
 
    def __repr__(self) -> str:
        return "Stationary_Battery_{current_Capacity}KWh".format(current_Capacity=self.current_Capacity)
    
    def charge(self, amount):
        self.current_Capacity += amount 
    
    def discharge(self, amount):
        self.current_Capacity -= amount 

    @property
    def kwh_price(self):
        return self.price_per_kWh

    @property
    def soc(self):
        return round(self.current_Capacity / self.battery_size,2)

    @property
    def charge_Rate(self):
        return self._charge_Rate

    @property
    def battery_size(self):
        return self._battery_size

    @property
    def current_Capacity(self):
        return self._current_Capacity


    @current_Capacity.setter
    def current_Capacity(self, value):
        self._current_Capacity = value
    
    @battery_size.setter
    def battery_size(self, value):
        self._battery_size = value