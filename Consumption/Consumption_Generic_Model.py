from Consumption.Consumption_Model import ML_Model
from keras.preprocessing.sequence import TimeseriesGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from keras.callbacks import EarlyStopping

class Consumption_Generic_Model(ML_Model):
    
    def __init__(self, modelPath="Consumption/Models/Generic", past_window=24, featuresNames = [], targetName = None):
        super().__init__(modelPath, past_window, featuresNames, targetName)
        self.x_scaler = self.load_model(self.modelPath + "/x_scaler.sav")
        self.y_scaler = self.load_model(self.modelPath + "/y_scaler.sav")
    
    
    def innit_Model(self):
        #OPTIMIZAVEL
        self.model = Sequential()
        self.model.add(LSTM(units=128, return_sequences=True,input_shape=(self.past_window, len(self.featuresNames))))
        self.model.add(LSTM(units=64))
        self.model.add(Dense(units = 1))
        self.model.compile(optimizer = 'adam', loss = 'mean_squared_error', metrics = 'mean_absolute_error')
    
    def do_train(self, train_generator, showplot=False):
        early_stopping = EarlyStopping(monitor="loss", 
                                    patience=2, 
                                    mode="min")
        
        history = self.model.fit(train_generator, 
                                    epochs=8,
                                    shuffle = False, 
                                    callbacks=[early_stopping],
                                    verbose=0
                                    )
    
    def train(self, df):
        x_train = self.x_scaler.transform(df[self.featuresNames].values)
        y_train = self.y_scaler.transform(df[self.targetName].values.reshape(-1,1))

        #Time series
        train_generator = TimeseriesGenerator(x_train, y_train, length=self.past_window, batch_size=64)
        self.do_train(train_generator)

    def predict_next(self, df):
        x_test = self.x_scaler.transform(df[self.featuresNames].iloc[-(self.past_window + 1):].values)
        y_test = [0 for i in range(self.past_window+1)] #doesnt matter
        test_generator = TimeseriesGenerator(x_test, y_test, length=self.past_window, batch_size=1)

        generic_prediction = self.y_scaler.inverse_transform(self.model.predict(test_generator))[0]
        generic_prediction = generic_prediction if generic_prediction >= 0 else 0
        return generic_prediction
