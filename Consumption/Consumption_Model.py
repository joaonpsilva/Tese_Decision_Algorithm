import pickle

class ML_Model:

    def __init__(self, modelPath=None, past_window=24):
        self.modelPath = modelPath
        self.model = None
        
        self.past_window = None
        self.featuresNames = []
        self.targetName = None

        try:
            self.model = self.load_model()
        except:
            self.innit_Model()
    
    def innit_Model(self):
        raise NotImplementedError

    def save_model(self):
        pickle.dump(self.model, open(self.modelPath, 'wb'))

    def load_model(self):
        return pickle.load(open(self.modelPath, 'rb'))