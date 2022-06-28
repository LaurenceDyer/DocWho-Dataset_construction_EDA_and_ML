import pandas as pd
import numpy as np
from pickle import load
import matplotlib.pyplot as plt

from nltk import word_tokenize          
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MaxAbsScaler
from sklearn.preprocessing import LabelEncoder

from sklearn.model_selection import GridSearchCV

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay

model = load(open("multiBinomial_ERA.sav", 'rb'))
selector = load(open('selector.pkl', 'rb'))
vectorizer = load(open("vectorizer.pkl", "rb"))
le = load(open("le.pkl","rb"))

allDat = pd.read_csv("Eras_for_Bayes.csv")

x_test = allDat["Script"]
y_test = allDat["Era"]

y_test = le.transform(y_test)

print("Vectorizing...")
x_test = vectorizer.transform(x_test).toarray()

print("Feature filtering...")
x_test = selector.transform(x_test).astype('float32')

print("Predicting...")
y_pred = model.predict(x_test)

print("Model accuracy")
print("\n", accuracy_score(y_pred, y_test))

print(classification_report(y_test, y_pred,target_names=["Classic", "Modern"]))
print("\n")
