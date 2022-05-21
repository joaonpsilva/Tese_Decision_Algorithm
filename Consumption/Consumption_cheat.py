class Consumption_Cheat:
    def __init__(self, past_window, fileNumber) -> None:

        self.f = open("cheats/cheat" + str(fileNumber) + ".txt", "r")
        self.i = 0
        self.past_window = past_window
    
    def new_Record(self, record):
        pass

    def get_Prediction(self):
        self.i+=1
        if self.i <= self.past_window:
            return None
        
        return float(self.f.readline())
        
        