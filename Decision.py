class Decision:

    def __init__(self, energy_From, energy_To, energy_amount):
        self._energy_From = energy_From
        self._energy_To = energy_To
        self._energy_amount = energy_amount

    @property
    def energy_From(self):
        return self._energy_From

    @property
    def energy_To(self):
        return self._energy_To

    @property
    def energy_amount(self):
        return self._energy_amount

    @energy_From.setter
    def energy_From(self, value):
        self._energy_From = value

    @energy_To.setter
    def energy_To(self, value):
        self._energy_To = value
    
    @energy_amount.setter
    def energy_amount(self, value):
        self._energy_amount = value