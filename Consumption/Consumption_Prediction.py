"""
Consumption Prediction class

Contains a generic and a specific model

Predicts energy consumption values in 1h time steps
"""
import pandas as pd
from Consumption.Consumption_Generic_Model import Consumption_Generic_Model
from Consumption.Consumption_Specific_Model import Consumption_Specific_Model
import json
from sklearn.metrics import mean_absolute_error

class Consumption_Prediction:

    def __init__(self, past_window=24, featuresNames = [], targetName = None):

        self.prediction = None
                
        self.load_details(past_window,featuresNames, targetName )

        #Create Instances of specific and generic models
        self.specific_Model = Consumption_Specific_Model(past_window=past_window, featuresNames = featuresNames, targetName = targetName)
        if self.best_model == "generic":
            self.generic_Model = Consumption_Generic_Model(past_window=past_window, featuresNames = featuresNames, targetName = targetName)

        self.hourIndex = 0

    def load_details(self, past_window,featuresNames, targetName):
        """Load Details from file or create them"""

        try:
            f = open("Consumption/Models/Consumption_Model_Details.json")
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
            self.userKnownDf  = pd.read_csv("Consumption/Models/UserKnowDf.csv", delimiter = ',')
        except:
            self.userKnownDf = pd.DataFrame(data={key:[] for key in featuresNames})
    
    def save_detais(self):
        """Save details in file NOT USED"""

        # Serializing json 
        d = { 
            "past_window": self.past_window,
            "featuresNames": self.self.featuresNames,
            "targetName": self.targetName,
            "best_model": self.best_model,
            "generic_Model_Predictions": self.generic_Model_Predictions,
            "specific_Model_Predicitos": self.specific_Model_Predicitons,
            }
        json_object = json.dumps(d, indent = 4)
        
        # Writing to sample.json
        with open("Consumption/Models/Consumption_Model_Details.json", "w") as outfile:
            outfile.write(json_object)
        
        #save
        self.userKnownDf.to_csv("Consumption/Models/UserKnowDf.csv", index=False)


    
    def append_record(self, record):
        """Receive true value from meter and append to known values"""

        #append record
        self.userKnownDf = self.userKnownDf.append(record[self.featuresNames])

        #remove older then 1 year values
        if len(self.userKnownDf) > 24*365:
            self.userKnownDf = self.userKnownDf.iloc[1:]
        
    
    def genericVSspecific(self):
        """Compares performance of specific vs generic models and selects the best"""

        #Specific model doesnt have enough predictions to compare
        if len(self.specific_Model_Predicitons) < 48:
            return "generic"

        #read true values
        true = self.userKnownDf[self.targetName].iloc[-48:].values
        
        #Calculate MAE valeus of both models for the last 48h
        generic_mae = mean_absolute_error(true, self.generic_Model_Predictions[-48])
        specific_mae = mean_absolute_error(true, self.specific_Model_Predicitons[-48])

        #select best model
        if generic_mae < specific_mae:
            return "generic"
        else:
            return "specific"
    

    def retrain(self):
        """
        Retrain model with more recent records
        """    

        #Specific Model
        self.specific_Model.train(self.userKnownDf)

        #Only train generic model if is still used
        if self.best_model == "generic":
            self.generic_Model.train(self.userKnownDf)
    


    def make_new_prediction(self):
        """Make prediction of next value"""
        
        #Specific Model doesnt not exist in the 1st week
        if self.hourIndex >= 7*24:
            specific_prediction = self.specific_Model.predict_next(self.userKnownDf)
            self.prediction = specific_prediction

        #Only use generic if it still is best model
        if self.best_model == "generic":
            generic_prediction = self.generic_Model.predict_next(self.userKnownDf)
            self.prediction = generic_prediction
        

        return self.prediction
    


    def new_Record(self, record):
        """Receive new record from meter"""
        
        self.hourIndex += 1

        #store record in dataframe
        self.append_record(record)
        

        #Check which model is the best currently
        if self.best_model == "generic":
            self.best_model = self.genericVSspecific()

        #Retrain models every week
        if self.hourIndex % (7*24) == 0:
            self.retrain()

        #Make new predictions
        if self.hourIndex > 24:
            self.make_new_prediction()
    

    def get_Prediction(self):
        return self.prediction
        

        
#___________IGNORE_______________
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
