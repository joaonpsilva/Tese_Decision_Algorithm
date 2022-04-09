class EV:
    
    def __init__(self, soc=0, charge_Rate=0, batterry_Threshold = 0.3):
        
        self._soc = soc
        self._charge_Rate = charge_Rate
        self._batterry_Threshold = batterry_Threshold
        self._departure_Time = None

    @property
    def soc(self):
        return self._soc

    @property
    def charge_Rate(self):
        return self._charge_Rate

    @property
    def batterry_Threshold(self):
        return self._batterry_Threshold

    @property
    def departure_Time(self):
        return self._departure_Time

    @soc.setter
    def soc(self, value):
        self._soc = value

    @charge_Rate.setter
    def charge_Rate(self, value):
        self._charge_Rate = value

    @batterry_Threshold.setter
    def batterry_Threshold(self, value):
        self._batterry_Threshold = value

    @departure_Time.setter
    def departure_Time(self, value):
        self._departure_Time = value
