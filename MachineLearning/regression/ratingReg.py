import pandas as pd
import numpy as np
from numpy import absolute
from numpy import arange
import pickle
import matplotlib.pyplot as plt

from numpy import mean
from numpy import std
from numpy import absolute

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
from category_encoders import TargetEncoder

from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score

pd.options.display.width = 0

ratDat = pd.read_csv("Rating_Reg.csv")
ratDat = ratDat.drop(columns="Unnamed: 0")

numCols = ["WordsInLine","Script","Scene","Location","Character","Runtime"]

nomCols = ["Writer","Director"]

labelCols = ["Rating"]

minmax = MinMaxScaler(feature_range = (0,10))
encoderW = TargetEncoder()
encoderD = TargetEncoder()
ohe = OneHotEncoder()

ratDat = ratDat.dropna()

x = ratDat.iloc[:,1:9]
y = ratDat.iloc[:,9]

x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.2, random_state=1337)

x_train['Writer'] = encoderW.fit_transform(x_train['Writer'], y_train)
x_train['Director'] = encoderD.fit_transform(x_train['Director'], y_train)
x_train[numCols] = minmax.fit_transform(x_train[numCols])

print(x_train)

grid = dict()
grid['alpha'] = arange(1e-10,1e-7,1e-9)

model=ElasticNet()
cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)

search = GridSearchCV(model, grid, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
results = search.fit(x_train, y_train)

print('MAE: %.3f' % results.best_score_)
print('Config: %s' % results.best_params_)

model=Lasso(alpha=1e-10)
model.fit(x_train,y_train)
print(x_train)
print(model.coef_)

x_test['Writer'] = encoderW.transform(x_test['Writer'])
x_test['Director'] = encoderD.transform(x_test['Director'])
x_test[numCols] = minmax.transform(x_test[numCols])
x_test = x_test.dropna()

y_pred = model.predict(x_test)

print(np.sqrt(mean_absolute_error(y_test,y_pred))) 
print(r2_score(y_test, y_pred))