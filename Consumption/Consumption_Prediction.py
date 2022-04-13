import pandas as pd
from Consumption_Generic_Model import Consumption_Generic_Model
from Consumption_Specific_Model import Consumption_Specific_Model
import json
from sklearn.metrics import mean_absolute_error

class Consumption_Prediction:

    def __init__(self, past_window=24, featuresNames = [], targetName = None):

        self.prediction = None
                
        self.load_details(past_window,featuresNames, targetName )

        self.specific_Model = Consumption_Specific_Model(past_window=past_window, featuresNames = featuresNames, targetName = targetName)

        if self.best_model == "generic":
            self.generic_Model = Consumption_Generic_Model(past_window=past_window, featuresNames = featuresNames, targetName = targetName)



    def load_details(self, past_window,featuresNames, targetName):
        try:
            f = open("Models/Consumption_Model_Details.json")
            info = json.load(f)
            f.close()

            self.past_window = int(info["past_window"])
            self.featuresNames = info["featuresNames"]
            self.targetName = info["targetName"]
            self.best_model = info["best_model"]
            self.generic_Model_Predictions = info["generic_Model_Predictions"]
            self.specific_Model_Predicitons = info["specific_Model_Predicitons"]
        except:
            self.past_window = past_window
            self.featuresNames = featuresNames
            self.targetName = targetName
            self.best_model = "generic"
            self.generic_Model_Predictions = []
            self.specific_Model_Predicitons = []
        
        try:
            self.userKnownDf  = pd.read_csv("Models/UserKnowDf", delimiter = ',')
        except:
            self.userKnownDf = pd.DataFrame(data={key:[] for key in featuresNames})
    
    def save_detais(self):
        # Serializing json 
        d = { 
            "past_window": self.past_window,
            "featuresNames": self.self.featuresNames,
            "targetName": self.targetName,
            "best_model": self.best_model,
            "generic_Model_Predictions": self.generic_Model_Predictions,
            "specific_Model_Predicitos": self.specific_Model_Predicitos,
            }
        json_object = json.dumps(d, indent = 4)
        
        # Writing to sample.json
        with open("Models/Consumption_Model_Details.json", "w") as outfile:
            outfile.write(json_object)
    
    def append_record(self, record):
        #append record
        self.userKnownDf = self.userKnownDf.append(record[self.featuresNames])
        if len(self.userKnownDf) > 24*365:
            self.userKnownDf = self.userKnownDf.iloc[1:]
        
        #save
        self.userKnownDf.to_csv("Models/UserKnowDf")

    
    def genericVSspecific(self):
        true = self.userKnownDf[self.targetName].iloc[-48:].values
        
        generic_mae = mean_absolute_error(true, self.generic_Model_Predictions[-48])
        specific_mae = mean_absolute_error(true, self.specific_Model_Predicitons[-48])

        if generic_mae < specific_mae:
            return "generic"
        else:
            return "specific"
    
    def retrain(self):

        self.specific_Model.train(self.userKnownDf)

        if self.best_model == "generic":
            self.generic_Model.train(self.userKnownDf)

    
    def new_Record(self, record):

        self.append_record(record)
        
        if self.best_model == "generic":
            self.best_model = self.genericVSspecific()

        self.retrain()

        self.make_new_prediction()

    
    
    def make_new_prediction(self):

        specific_prediction = self.specific_Model.predict_next(self.userKnownDf)
        self.prediction = specific_prediction

        if self.best_model == "generic":
            generic_prediction = self.generic_Model.predict_next(self.userKnownDf)
            self.prediction = generic_prediction
        

        return self.prediction

        

        

if __name__ == "__main__":
    import os
    print("----------------------")

    directory = "../../datsets/LCL_Data_Transformed/test"
    filename = sorted(os.listdir(directory))[0]

    featuresNames = ['use', 'hour', 'weekday']
    targetName = ['use']
    past_window = 24

    f = os.path.join(directory, filename)
    df = pd.read_csv(f, delimiter = ',')

    consumption_Prediction = Consumption_Prediction(past_window, featuresNames, targetName)

    for index, row in df.iterrows():
        #Read new values
        
        consumption_Prediction.new_Record(row)
        break
