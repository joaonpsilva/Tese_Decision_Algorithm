import pandas as pd

def removeSecs(a):
    return a[:13]

class Production_Meter:

    def __init__(self, startDate, solar_Panel_Area=1, file="Portugal"):
        
        self._solar_Panel_Area = solar_Panel_Area

        self.df = pd.read_csv("Production/" + file + "_Solar.csv", delimiter = ',')

        self.df['PeriodStart'] = self.df.apply(lambda row : removeSecs(row['PeriodStart']), axis = 1)
        self.df['PeriodEnd'] = self.df.apply(lambda row : removeSecs(row['PeriodEnd']), axis = 1)

        self.df['PeriodStart']= pd.to_datetime(self.df['PeriodStart'], format='%Y-%m-%dT%H')
        self.df['PeriodEnd']= pd.to_datetime(self.df['PeriodEnd'], format='%Y-%m-%dT%H')

        mask = (self.df['PeriodStart'] >= startDate)
        self.df = self.df.loc[mask]

        self.i = 0
    
    @property
    def solar_Panel_Area(self):
        return self._solar_Panel_Area

    @solar_Panel_Area.setter
    def solar_Panel_Area(self, value):
        self._solar_Panel_Area = value

    def get_Meter_Value(self):
        
        #https://www.theecoexperts.co.uk/solar-panels/how-much-electricity

        #"irradiação normal direta no intervalo em watts por metro quadrado"
        dni = self.df.iloc[self.i]["Dni"]
        self.i += 1

        #"valores mais comuns para a performance de células fotovoltaicas"
        r = 0.15

        #"desprezável o fator de idade do painel, ou seja, não é considerada a deterioração do mesmo ao longo do tempo"
        p = 0.8
        E = self._solar_Panel_Area * r * dni * p

        return E / 1000

if __name__ == "__main__":
    from datetime import datetime, timedelta


    timestamp = "2012-10-20T09:00:00Z"
    timestamp = datetime.strptime(timestamp[:13], '%Y-%m-%dT%H')
    production_Meter = Production_Meter(timestamp)
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())
    print(production_Meter.make_Prediction())


