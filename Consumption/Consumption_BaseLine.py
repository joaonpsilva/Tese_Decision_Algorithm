class Consumption_BaseLine:
    def __init__(self, target):
        self.target = target

    def new_Record(self, record):
        self.last = record[self.target]
    
    def get_Prediction(self):
        return self.last