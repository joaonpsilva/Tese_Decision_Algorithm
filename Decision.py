class Decision:

    def __init__(self, obj, mode, energy_amount):
        self._obj = obj
        self._mode = mode
        self._energy_amount = energy_amount

    @property
    def obj(self):
        return self._obj

    @property
    def mode(self):
        return self._mode

    @property
    def energy_amount(self):
        return self._energy_amount

    @obj.setter
    def obj(self, value):
        self._obj = value

    @mode.setter
    def mode(self, value):
        self._mode = value
    
    @energy_amount.setter
    def energy_amount(self, value):
        self._energy_amount = value