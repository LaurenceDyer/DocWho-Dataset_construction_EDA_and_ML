import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import ConfusionMatrixDisplay

allDat = pd.read_csv("allDat_for_Bayes_noFour.csv")
allDat = allDat.loc[:, ~allDat.columns.str.contains('^Unnamed')]
allDat = allDat.loc[:,~allDat.columns.str.contains('^Script_lemm$')]

#Split data into train and test sets, separate features and labels
x = allDat['Script']
y = allDat['Character']

print("DOCTOR4 REMOVED!")

print("Splitting test and train data...")
x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.25, random_state=42, stratify=y)

print("Vectorizing...")
#Vectorize each data set
vectorizer = TfidfVectorizer(ngram_range = (1,2), stop_words="english")
x_train = vectorizer.fit_transform(x_train).toarray()
x_test = vectorizer.transform(x_test).toarray()

#scale datasets for learning
print("Scaling...")
sc = MinMaxScaler() 
x_train = sc.fit_transform(x_train)
x_test = sc.fit_transform(x_test)


#generate model
print("Fitting Model...")
model = MultinomialNB()
model.fit(x_train, y_train)

print("Predicting...")
y_pred = model.predict(x_test)

print("Model accuracy with parameter tuning:")

print("\n", accuracy_score(y_pred, y_test))

print(classification_report(y_test, y_pred,target_names=["DOCTOR1", "DOCTOR10", "DOCTOR11", "DOCTOR12", "DOCTOR2", "DOCTOR3"]))
print("\n")

print("Let's predict some phrases: \n")

print('Young woman bring me my cane')
print(model.predict(vectorizer.transform(['Young woman bring me my cane'])))
print("\n")

print('There\'s only room for one timelord on this planet')
print(model.predict(vectorizer.transform(['There\'s only room for one timelord on this planet'])))
print("\n")

print('I am become death, destroyer of worlds')
print(model.predict(vectorizer.transform(['There\'s only room for one timelord on this planet'])))
print("\n")

print('The meek shall inherit the earth')
print(model.predict(vectorizer.transform(['The meek shall inherit the earth'])))
print("\n")

print('If you change your mind, I\'m the first in line, Honey I\'m still free, Take a chance on me, If you need me, let me know, gonna be around, If you\'ve got no place to go, if you\'re feeling down, If you\'re all alone when the pretty birds have flown, Honey I\'m still free, Take a chance on me, Gonna do my very best and it ain\'t no lie, If you put me to the test, if you let me try')
print(model.predict(vectorizer.transform(['If you change your mind, I\'m the first in line, Honey I\'m still free, Take a chance on me, If you need me, let me know, gonna be around, If you\'ve got no place to go, if you\'re feeling down, If you\'re all alone when the pretty birds have flown, Honey I\'m still free, Take a chance on me, Gonna do my very best and it ain\'t no lie, If you put me to the test, if you let me try'])))
print("\n")
