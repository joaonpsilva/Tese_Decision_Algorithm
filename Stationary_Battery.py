class Stationary_Battery:

    def __init__(self, max_Capacity = 100):
        
        self._max_Capacity = max_Capacity
        self._current_Capacity = 0
    
    def __repr__(self) -> str:
        return "Stationary_Battery_{current_Capacity}KWh".format(current_Capacity=self.current_Capacity)

    @property
    def max_Capacity(self):
        return self._max_Capacity

    @property
    def current_Capacity(self):
        return self._current_Capacity

    @max_Capacity.setter
    def max_Capacity(self, value):
        self._max_Capacity = value

    @current_Capacity.setter
    def current_Capacity(self, value):
        self._current_Capacity = value