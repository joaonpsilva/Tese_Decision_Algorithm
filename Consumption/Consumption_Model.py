"""Base ML Model class

parent class to specific and generic models"""

import pickle

class ML_Model:

    def __init__(self, modelPath="", past_window=24, featuresNames = [], targetName = None):
        self.modelPath = modelPath
        self.model = None
        
        self.past_window = past_window
        self.featuresNames = featuresNames
        self.targetName = targetName

        try:
            self.model = self.load_model(self.modelPath + "/model.sav")
        except:
            self.innit_Model()
    
    def innit_Model(self):
        raise NotImplementedError

    def save_model(self, model, filename):
        pickle.dump(model, open(filename, 'wb'))

    def load_model(self, filename):
        return pickle.load(open(filename, 'rb'))