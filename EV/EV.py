from Battery import Battery

class EV:
    
    def __init__(self, soc=0, battery_size = 24, charge_Rate = 3, batterry_Threshold = 0):
        
        self._batterry_Threshold = batterry_Threshold
        self._departure_Time = None
        self._battery = Battery(soc, battery_size, charge_Rate, battery_price=5000)

    
    def __repr__(self) -> str:

        return "EV - Soc:{soc}, batterry_Threshold:{batterry_Threshold}, departure_Time:{departure_Time}"\
            .format(soc=self.battery.soc,batterry_Threshold=self.batterry_Threshold,departure_Time=self.departure_Time)
        
    
    def charge(self, amount):
        return self.battery.charge(amount)
    
    def discharge(self, amount):
        return self.battery.discharge(amount)


    @property
    def batterry_ThresholdKWH(self):
        return self._batterry_Threshold * self.battery.battery_size
    

    @property
    def batterry_Threshold(self):
        return self._batterry_Threshold

    @property
    def departure_Time(self):
        return self._departure_Time
    
    @property
    def battery(self):
        return self._battery


    @batterry_Threshold.setter
    def batterry_Threshold(self, value):
        self._batterry_Threshold = value

    @departure_Time.setter
    def departure_Time(self, value):
        self._departure_Time = value
    
    @battery.setter
    def battery(self, value):
        self._battery = value
