import pandas as pd
import numpy as np
import pickle
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

np.set_printoptions(threshold=np.inf)

##Input data outputted from R
#allDat = pd.read_csv("Eras_for_Bayes.csv")
#allDat = allDat.loc[:, ~allDat.columns.str.contains('^Unnamed')]
#allDat = allDat.loc[:,~allDat.columns.str.contains('^Script_lemm$')]
#
##Subsample huge dataframe - Vectorizing this tkes more spcae than I have available
#allDat_classic = allDat[allDat["Era"] == "Classic"]
#allDat_modern = allDat[allDat["Era"] == "Modern"]
#
#allDat_classic = allDat_classic.sample(20000)
#allDat_modern = allDat_modern.sample(20000)
#
#allDat = pd.concat([allDat_classic,allDat_modern])

#allDat.to_csv("subSampled_allDat.csv")

stop_words = set(stopwords.words('english')) 
allDat = pd.read_csv("subSampled_allDat.csv")

#Split data into train and test sets, separate features and labels
x = allDat['Script']
y = allDat['Era']

print("Splitting test and train data...")
x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.25, random_state=42, stratify=y)

print("Encoding labels...")
le = LabelEncoder()
le.fit(y)
y_train = le.transform(y_train)
y_test = le.transform(y_test)

pickle.dump(le, open("le.pkl", "wb"))

print("Vectorizing...")
#Vectorize each data set
class LemmaTokenizer:
    ignore_tokens = [',', '.', ';', ':', '"', '``', "''", '`']
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if t not in self.ignore_tokens]

tokenizer=LemmaTokenizer()
token_stop = tokenizer(' '.join(stop_words))

vectorizer = TfidfVectorizer(ngram_range = (1,1))#, tokenizer=tokenizer)

x_train = vectorizer.fit_transform(x_train).toarray()
x_test = vectorizer.transform(x_test).toarray()
pickle.dump(vectorizer, open('vectorizer.pkl', 'wb'))

print(x_train.shape)

print("Selecting features...")
#Feature selection
selector = SelectKBest(chi2, k=min(10000, x_train.shape[1]))
selector.fit(x_train, y_train)

x_train = selector.transform(x_train).astype('float32')
x_test = selector.transform(x_test).astype('float32')
pickle.dump(selector, open('selector.pkl', 'wb'))

#print("Scaling...")
##scale datasets for learning
#sc = MaxAbsScaler() 
#x_train = sc.fit_transform(x_train)
#x_test = sc.transform(x_test)

#generate model
model = MultinomialNB()

print("Fitting Model...")
model.fit(x_train, y_train)

#process test set
print("Predicting...")
y_pred = model.predict(x_test)

print("Model accuracy")
print("\n", accuracy_score(y_pred, y_test))

print(classification_report(y_test, y_pred,target_names=["Classic", "Modern"]))
print("\n")

print("Dumping")
pickle.dump(model, open('multiBinomial_ERA.sav', 'wb'))

confusion_matrix = confusion_matrix(y_test, y_pred, normalize='all')

print(confusion_matrix)

display = ConfusionMatrixDisplay(confusion_matrix).plot()

print("Let's predict some phrases: \n")

print("The world doesn't revolve around screens, and you'd be better off spending time outdoors")
print(le.inverse_transform(model.predict(selector.transform(vectorizer.transform(["The world doesn't revolve around Screens, and you'd be better off spending time outdoors"])))))
print("\n")

print("If the daleks make it out of the timelock then the universe is surely doomed")
print(le.inverse_transform(model.predict(selector.transform(vectorizer.transform(["If the daleks make it out of the timelock then the universe is surely doomed"])))))
print("\n")

print("Rock and roll is here to stay'")
print(le.inverse_transform(model.predict(selector.transform(vectorizer.transform(["Rock and roll is here to stay'"])))))
print("\n")

print("All are equal, but some are more equal than others")
print(le.inverse_transform(model.predict(selector.transform(vectorizer.transform(["All are equal, but some are more equal than others"])))))
print("\n")

print("I\'ve seen that on facebook, let me call my mum and tell her")
print(le.inverse_transform(model.predict(selector.transform(vectorizer.transform(["I\'ve seen that on facebook, let me call my mum and tell her"])))))
print("\n")

print("I love watching TV with you love, but do go and make a cuppa")
print(le.inverse_transform(model.predict(selector.transform(vectorizer.transform(["I love watching TV with you love, but do go and make a cuppa"])))))
print("\n")


#alphas = [0.001,0.01,0.1,1,10,100,1000]
#
#parameters = {'alpha': (alphas)}
#
##perform grid search
#gs_model = GridSearchCV(model, parameters, n_jobs=-1)
#gs_model = gs_model.fit(x_train, y_train)
#
#print(gs_model.best_score_)
#print(gs_model.best_params_)
#
#
#print(gs_model.cv_results_)
#print(gs_model.best_estimator_)


print("Done")