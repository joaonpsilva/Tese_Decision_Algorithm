"""
Consumption Prediction baseline

Implements same methods than Consumption prediction but 
predicts last observed value
"""
class Consumption_BaseLine:
    def __init__(self, target):
        self.target = target

    def new_Record(self, record):
        self.last = record[self.target]
    
    def get_Prediction(self):
        return self.last