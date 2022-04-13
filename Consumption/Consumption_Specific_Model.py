from Consumption_Model import ML_Model
from sklearn.preprocessing import StandardScaler
from keras.preprocessing.sequence import TimeseriesGenerator
from sklearn.svm import SVR


class Consumption_Specific_Model(ML_Model):
    
    def __init__(self, modelPath="Models/Specific", past_window=24, featuresNames = [], targetName = None):
        super().__init__(modelPath, past_window, featuresNames, targetName)
        self.x_scaler = StandardScaler()
        self.y_scaler = StandardScaler()
    
    
    def innit_Model(self):
        self.model = SVR(kernel = "rbf")
    
    def train(self, df):
        self.innit_Model()

        x_train = self.x_scaler.fit_transform(df[self.featuresNames].values)
        y_train = self.y_scaler.fit_transform(df[self.targetName].values.reshape(-1,1))
        train_generator = TimeseriesGenerator(x_train, y_train, length=self.past_window, batch_size=1)
        
        x_train = [arr[0].flatten() for arr in train_generator]
        y_train = [arr[1].flatten() for arr in train_generator]

        self.model.fit(x_train, y_train)


    def predict_next(self, df):
        x_test = self.x_scaler.transform(df[self.featuresNames].iloc[-(self.past_window + 1):].values)
        y_test = [0 for i in range(self.past_window+1)] #doesnt matter
        test_generator = TimeseriesGenerator(x_test, y_test, length=self.past_window, batch_size=1)
        x_test = [arr[0].flatten() for arr in test_generator]

        specific_prediction = self.y_scaler.inverse_transform(self.model.predict(x_test))[0]
        specific_prediction = specific_prediction if specific_prediction >= 0 else 0
        return specific_prediction
